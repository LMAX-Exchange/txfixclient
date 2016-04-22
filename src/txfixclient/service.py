#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
import io
import itertools
import json
import copy
from datetime import datetime, timedelta
from collections import OrderedDict
from txfixclient import messages
from txfixclient.ifixclient import IFixClient
from txfixclient.spec import Spec
from txfixclient.logging import passThroughFileLogObserver
from hdrh.histogram import HdrHistogram
from twisted.application import service
from twisted.internet import reactor, task
from twisted.logger import Logger, textFileLogObserver
from zope.interface import implementer
import platform
import os

log = Logger()


def format_time(datetime_obj):
    return datetime_obj.strftime("%Y%m%d-%H:%M:%S.%f")[:-3]


def parse_time(fixtime):
    return datetime.strptime(fixtime, "%Y%m%d-%H:%M:%S.%f")


def timedelta_milliseconds(td):
    return td.days*86400000 + td.seconds*1000 + td.microseconds/1000


@implementer(IFixClient)
class FixClientService(service.Service):
    _log = Logger()
    encoding = 'ascii'

    def __init__(self, config):
        self.config = config
        self.spec = Spec(config['spec'])
        self._seqnum = itertools.count(1)
        self._test_request_id = itertools.count(1)
        self.test_requests = dict()
        self.version = self.spec.root.attrib
        self.BeginString = '.'.join([
            self.version['type'],
            self.version['major'],
            self.version['major']
        ])
        self.SenderCompID = self.config['sender_comp_id']
        self.TargetCompID = self.config['target_comp_id']
        self.EncryptMethod = 0
        self.hb_int = int(self.config['heartbeat_int'])
        self.stats_interval = int(self.config['metrics_interval'])
        if os.path.isdir(self.config['statsdir']):
            self.stats_dir = self.config['statsdir']
        else:
            raise Exception("Error: statsdir not found: '{0!s}'".format(self.config['statsdir']))

        # stats counters
        self.stats = OrderedDict({
            'msg_tx_count': 0,
            'msg_rx_count': 0,
            'msg_tx_bytes': 0,
            'msg_rx_bytes': 0,
        })

    def reset(self):

        self._seqnum = itertools.count(1)
        self._test_request_id = itertools.count(1)
        self.test_requests = dict()
        self.stats = OrderedDict({
            'msg_tx_count': 0,
            'msg_rx_count': 0,
            'msg_tx_bytes': 0,
            'msg_rx_bytes': 0,
        })



    def stats_setup(self):

        self.stats_snapshot_previous = None
        self.interval_histogram = HdrHistogram(1, 10000000, 3)
        self.ttl_histogram = HdrHistogram(1, 10000000, 3)
        self.msglag_histogram = HdrHistogram(1, 10000000, 3)

        namespace = "stats_{0!s}_{1!s}_depth_{2!s}".format(platform.node(),
                                        self.SenderCompID,
                                        self.config['market_depth'])
        filename = os.path.join(self.stats_dir,
                namespace+datetime.strftime(datetime.utcnow(), "_%Y%m%d%H%M%S")+'.log')

        self._stats_logger = Logger(
            observer=passThroughFileLogObserver(io.open(filename, "a")),
            namespace='')
        self.stats_loop = task.LoopingCall(self.log_stats)
        self.stats_loop.start(self.stats_interval)

    def log_stats(self):

        stats_snapshot = self.stats.copy()

        tmp_stats = OrderedDict()
        if self.stats_snapshot_previous:
            for k in stats_snapshot.keys():
                tmp_stats[k+'_rate'] = (float(stats_snapshot[k]) - float(self.stats_snapshot_previous[k])) / \
                    float(self.stats_interval)
        else:
            for k in stats_snapshot.keys():
                tmp_stats[k+'_rate'] = stats_snapshot[k]
        self.stats_snapshot_previous = stats_snapshot

        # copy and reset latency histogram
        ih = copy.copy(self.interval_histogram)
        self.interval_histogram = HdrHistogram(1, 10000000, 3)

        latency = OrderedDict()
        latency['latency_max'] = ih.get_max_value()
        latency['latency_min'] = ih.get_min_value()
        latency['latency_mean'] = ih.get_mean_value()
        for x in [99.90, 99.00]:
            latency['latency_{0:.2f}'.format(x)] = ih.get_value_at_percentile(x)

        # copy and reset ttl histogram
        th = copy.copy(self.ttl_histogram)
        self.ttl_histogram = HdrHistogram(1, 10000000, 3)
        ttl = OrderedDict()
        ttl['ttl_max'] = th.get_max_value()
        ttl['ttl_min'] = th.get_min_value()
        ttl['ttl_mean'] = th.get_mean_value()
        for x in [99.90, 99.00]:
            ttl['ttl_{0:.2f}'.format(x)] = th.get_value_at_percentile(x)

        # copy and reset ttl histogram
        #ml = copy.copy(self.msglag_histogram)
        #self.msglag_histogram = HdrHistogram(1, 10000000, 3)
        #mlag = OrderedDict()
        #mlag['message_lag_max'] = ml.get_max_value()
        #mlag['message_lag_min'] = ml.get_min_value()
        #mlag['message_lag_mean'] = ml.get_mean_value()
        #mlag['message_lag_stddev'] = ml.get_stddev()
        #for x in [99.99, 99.95, 99.00, 95.00, 90.00]:
        #    mlag['message_lag_%.2f' % x] = ml.get_value_at_percentile(x)

        data = OrderedDict()
        data.update(stats_snapshot)
        data.update(tmp_stats)
        data.update(latency)
        data.update(ttl)
        #data.update(mlag)
        data.update({'timestamp': format_time(datetime.utcnow())})

        self._stats_logger.info("{data}", data=json.dumps(data))

    def next_test_request_id(self):
        return self._test_request_id.next()

    def next_msg_seq_num(self):
        return self._seqnum.next()

    def startService(self):
        log.debug("xxxxxxxxxxx Starting FixClientService xxxxxxxxxxxxxxx")
        service.Service.startService(self)
        self.stats_setup()

    def stopService(self):
        log.debug("xxxxxxxxxxx Stopping FixClientService xxxxxxxxxxxxxxx")
        service.Service.stopService(self)

    def clientConnected(self, proto):
        self._proto = proto
        self.reset()
        self.call_Logon()

    def sendMessage(self, msg):
        msg_type = self.spec.get_message_by_msgtype(msg.type).attrib['name']
        # msg_type = 'Out'
        log.debug("Transmit {msg_type}: {msg}", msg_type=msg_type,
                       msg=msg.as_string())
        self._proto.sendMessage(msg)
        self.stats['msg_tx_count'] += 1
        self.stats['msg_tx_bytes'] += msg.length
        self._last_message_sent = datetime.utcnow()

    def handleMessage(self, msg):
        self.stats['msg_rx_count'] += 1
        self.stats['msg_rx_bytes'] += msg.length

        msg_type = self.spec.get_message_by_msgtype(msg.type).attrib['name']
        servertime = parse_time(msg.get_tag(52)[0][1])
        now = datetime.utcnow()
        delta = timedelta_milliseconds(now - servertime)
        self.interval_histogram.record_value(delta)

        # record message creation to being takeno off the wire time
        self.msglag_histogram.record_value(timedelta_milliseconds(msg.created_at - msg.recieved_at))
        log.debug("Received {msg_type}: Remote time:{servertime}, "
                "Localtime:{now}, Latency:{delta}ms, msg.created_at:"
                "{created_at}, msg.recieved_at {recieved_at},  {msg}",
                       msg_type=msg_type,
                       msg=msg.as_string(), servertime=servertime, now=now,
                       created_at=msg.created_at, recieved_at=msg.recieved_at,
                       delta=delta)

        method = getattr(self, "handle_{0!s}".format(msg_type), None)

        #try:
        if method is not None:
            method(msg)
        else:
            self.handle_unknown(msg_type, msg)
        #except Exception as e:
        #    log.debug("{type}: {error}", type=type(e), error=e)
        #    log.debug("Do not know what to do with {msg_type}: {data}",
        #                   data=msg.as_string(), msg_type=msg_type)

    def handle_unknown(self, msg_type, msg):
        raise NotImplementedError(msg_type, msg.as_string())

    # Fix messages

    def call_Logon(self):
        msg = messages.Logon(self)
        self.sendMessage(msg)

    def handle_Logon(self, msg):
        log.debug("Logon: success")
        self.call_Heartbeat()
        self.testreq_loop = task.LoopingCall(self.call_TestRequest)
        self.testreq_loop.start(1)
        self.mdSubscribe(self.config['instrument_id'],
                         self.config['market_depth'],
                         self.config['instrument_id'])

    def handle_Logout(self, msg):
        log.debug("Logout: {reason}", reason=msg.get_tag(58)[0][1])

        # self.call_Heartbeat()

    def call_Heartbeat(self):
        time_since_last_message  = datetime.utcnow() - self._last_message_sent
        if  time_since_last_message > timedelta(seconds=self.hb_int):
            msg = messages.Heartbeat(self)
            self.sendMessage(msg)
        reactor.callLater(self.hb_int, self.call_Heartbeat)

    def handle_Heartbeat(self, msg):
        test_req_id = 0
        try:
            test_req_id = int(msg.get_tag(112)[0][1])
        except:
            pass

        if test_req_id > 0:
            senttime = self.test_requests[test_req_id]
            servertime = parse_time(msg.get_tag(52)[0][1])
            localtime = datetime.utcnow()
            latency = timedelta_milliseconds(localtime - servertime)
            ttl = timedelta_milliseconds(localtime - self.test_requests[test_req_id])
            self.ttl_histogram.record_value(ttl)
            log.debug(
                "senttime:{senttime}, servertime:{servertime}, localtime:{localtime}, latency:{latency}, ttl:{ttl}ms",
                senttime=senttime,
                servertime=servertime,
                localtime=localtime,
                latency=latency,
                ttl=ttl
                )
            del self.test_requests[test_req_id]

    def call_TestRequest(self):
        # TODO: measure time round trip with test requests
        msg = messages.TestRequest(self)
        self.test_requests[msg.get_tag(112)[0][1]] = parse_time(msg.get_tag(52)[0][1])
        self.sendMessage(msg)

    def handle_TestRequest(self, msg):

        pass

    def mdSubscribe(self, MDReqID=4001, MarketDepth=1, SecurityID=4001):

        msg = messages.MarketDataRequest(self,
                                         MDReqID,
                                         1, # subscribe
                                         MarketDepth,
                                         SecurityID,
                                         )
        self.sendMessage(msg)

    def handle_MarketData(self, msg):
        pass

    def handle_MarketDataRequestReject(self, msg):
        log.debug("MarketDataRequestReject: {reason}",
                reason=msg.get_tag(58)[0][1])

    def handle_MarketDataSnapshotFullRefresh(self, msg):
        # log.debug("MarketDataSnapshotFullRefresh: {msg}", msg=msg)
        pass


