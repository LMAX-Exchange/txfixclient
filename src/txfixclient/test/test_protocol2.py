

from twisted.trial import unittest
from zope.interface import implementer
from twisted.test import proto_helpers
from twisted.internet.protocol import ReconnectingClientFactory
from txfixclient.protocol import FixTagReceiver, FixMessageReceiver, \
    IFixClientFactory
from txfixclient.message import FixMessage


class FixTagReceiverTester(FixTagReceiver):

    MAX_TAG_LENGTH = 20

    tags = list()

    def tagReceived(self, tag):
        self.tags.append(tag)


class FixTagReceiverTestCase(unittest.TestCase):

    def setUp(self):
        self.transport = proto_helpers.StringTransport()
        self.proto = FixTagReceiverTester()
        self.proto.makeConnection(self.transport)

    def test_ReceiveFixTag(self):
        expected = [
            b'8=FIX.4.4',
            b'9=115',
            b'35=A',
            ]

        buf = b'8=FIX.4.4\x019=115\x0135=A\x0149=sndr'
        self.proto.dataReceived(buf)
        self.assertEqual(self.proto.tags, expected)
        # this test does nothing

    def test_TagTooLong(self):
        buf = b'8=FIX.4.4\x019=115\x0135=A\x0149=aaaaaaaaaaaaaaaaaaaaaaaaaaaaa'
        self.assertRaises(Exception, self.proto.dataReceived, buf)


class FixMessageReceiverTester(FixMessageReceiver):

    messages = list()

    def messageReceived(self, message):
        self.messages.append(message)




@implementer(IFixClientFactory)
class FixClientFactoryTester(ReconnectingClientFactory):

    ''''''

    def clientConnected(self, message):
        pass

    def handleMessage(self, message):
        pass


class FixMessageReceiverTestCase(unittest.TestCase):
    # skip = "This  is broken and needs fixing"

    def setUp(self):
        factory = FixClientFactoryTester()
        factory.protocol = FixMessageReceiverTester
        self.transport = proto_helpers.StringTransport()
        self.proto = factory.buildProtocol(('127.0.0.1', 0))
        self.proto.makeConnection(self.transport)

    def test_ReceiveFixMessage(self):

        fix_tags = [
            b'8=FIX.4.4',
            b'9=115',
            b'35=A',
            b'49=sndrcompid',
            b'56=tgtcompid',
            b'34=1',
            b'52=20160331-15:52:08.508',
            b'98=0',
            b'108=2',
            b'141=Y',
            b'553=sndrcompid',
            b'554=$ecretP4ssword',
            b'10=110',
        ]

        for i in range(0, len(fix_tags)):
            self.proto.tagReceived(fix_tags[i])

        self.assertEqual(len(self.proto.messages), 1)

        msg = self.proto.messages[0]
        self.assertIsInstance(msg, FixMessage)
        self.assertEqual(msg.checksum, '110')
