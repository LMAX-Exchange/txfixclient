# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#

"""

"""

from datetime import datetime
from twisted.logger import Logger
from txfixclient.message import FixMessage
log = Logger()


def format_time(datetime_obj):
    return datetime_obj.strftime("%Y%m%d-%H:%M:%S.%f")[:-3]


def _message_header(client, msgtype):

    BeginString = client.BeginString
    BodyLength = 0
    MsgType = client.spec.get_message_by_name(msgtype).attrib['msgtype']
    SenderCompID = client.SenderCompID
    TargetCompID = client.TargetCompID
    MsgSeqNum = client.next_msg_seq_num()
    SendingTime = format_time(datetime.utcnow())

    header_vals = [
        BeginString,
        BodyLength,
        MsgType,
        SenderCompID,
        TargetCompID,
        MsgSeqNum,
        SendingTime,
    ]
    header_tags = [int(client.spec.get_field_by_name(header['name']).attrib['number']) for header in client.spec.list_header_required('Y')]
    msg_header = zip(header_tags, header_vals)
    return msg_header



class MyMessage(FixMessage):

    def __init__(self, client):
        super(MyMessage, self).__init__()

        headers = [
            (8, client.BeginString),
            (9, 0),
            (35, client.spec.get_message_by_name(self.__class__.__name__).attrib['msgtype']),
            (49, client.SenderCompID),
            (56, client.TargetCompID),
            (34, client.next_msg_seq_num()),
            (52, format_time(datetime.utcnow())),
        ]

        self.append_tags(headers)



class Heartbeat(FixMessage):

    def __init__(self, client):
        super(Heartbeat, self).__init__()
        self.append_tags(_message_header(client, self.__class__.__name__))


class TestRequest(FixMessage):

    def __init__(self, client):
        super(TestRequest, self).__init__()
        self.append_tags(_message_header(client, self.__class__.__name__))
        self.append_tag(112, client.next_test_request_id())


class Logon(FixMessage):

    def __init__(self, client):
        super(Logon, self).__init__()
        self.append_tags(_message_header(client, self.__class__.__name__))

        msg_body = [
            (98, client.EncryptMethod),
            (108, client.hb_int),
            (141, 'Y'),
            (553, client.config['sender_comp_id']),
            (554, client.config['password']),
            ]
        self.append_tags(msg_body)


class MarketDataRequest(FixMessage):

    def __init__(self, client,
                 MDReqID,
                 SubscriptionRequestType,
                 MarketDepth,
                 SecurityID):
        super(MarketDataRequest, self).__init__()
        self.append_tags(_message_header(client, self.__class__.__name__))

        msg_body = [
            (262, MDReqID),  # STRING  ;
            (263, SubscriptionRequestType),  # CHAR enum="2" description="UNSUBSCRIBE", enum="1" description="SNAPSHOTUPDATE"
            (264, MarketDepth),  # INT
            (265, 0),  # INT
            (146, 1),  # NUMINGROUP  = 1 ; count of the following security
            (48, SecurityID),  # STRING ; same as MDReqID ?
            (22, 8),  # STRING enum="8" description="EXCHSYMB"
            (267, 2), # NUMINGROUP - Number of the following tag
            (269, 0),  # CHAR =0 ; enum="1" description="OFFER", enum="0" description="BID" i
            (269, 1),  # CHAR =1 ; enum="1" description="OFFER", enum="0" description="BID"
        ]

        self.append_tags(msg_body)

