# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#

from twisted.python import usage
from twisted.internet import ssl
from twisted.application import internet, service
from txfixclient.protocol import FixClientFactory
from txfixclient.service import FixClientService
from txfixclient.spec import Spec
import os

class Options(usage.Options):
    synopsis = "[options]"
    longdesc = 'Fix Client.'
    optParameters = [
        ["hostname", "h", "localhost", "Set the host to connect to."],
        ["port", "p", 8443, "Set the destination port."],
        ['spec', 's', None, 'Fix xml spec file'],
        ['heartbeat_int', 'H', 30, 'Heartbeat Interval'],
        ['target_comp_id', 'T', None, 'TargetCompId'],
        ['sender_comp_id', 'S', None, 'SenderCompID'],
        ['password', 'P', None, 'Password'],
        ['instrument_id', 'i', None, 'Instrument/security id'],
        ['market_depth', 'd', 1, 'Market depth'],
        ['metrics_interval', 'm', 5, 'Interval to record metrics (sec)'],
        ['statsdir', 'o', os.getcwd(), 'irectory to stora stats output'],
    ]
    compData = usage.Completions(
        optActions={"hostname": usage.CompleteHostnames()}
        )

#    def postOptions(self):
#        for opt in ['spec', 'target_comp_id', 'sender_comp_id', 'password',
#                'instrument_id']:
#            if not self[opt]:
#                raise usage.UsageError, "Must set '%s' for this to work" % opt



def makeService(config):
    # finger on port 79
    msvc = service.MultiService()

    fix_spec = Spec(config['spec'])

    fix_service = FixClientService(config)
    fix_service.setName('txfixclient')
    fix_service.setServiceParent(msvc)
    factory = FixClientFactory(fix_service)
    factory.spec = fix_spec
    factory.maxDelay = 300
    tcp_service = internet.SSLClient(
        config['hostname'],
        int(config['port']),
        factory,
        ssl.ClientContextFactory()
        )
    tcp_service.setServiceParent(msvc)
    return msvc

