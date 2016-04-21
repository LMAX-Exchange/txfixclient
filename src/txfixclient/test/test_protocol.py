
from twisted.internet import protocol
from twisted.trial.unittest import TestCase
from twisted.test import proto_helpers
from txfixclient.protocol import FixTagReceiver, FixMessageReceiver


class FixTagReceiverTester(FixTagReceiver):

    tags = list()

    def tagReceived(self, tag):
        self.tags.append(tag)


class FixTagReceiverTests(TestCase):

    fix_buffers = [
        b'8=FIX.4.4\x019=113\x0135=A\x0149=sndrcom',
        b'pid\x0156=tgtcompid\x0134=',
        b'1\x0152=20160331-15:52:08.508\x0198=0\x01108=2\x011',
        b'41=Y\x01553=sndrcompid\x01554=$ecretP4ssword\x01',
        b'10=110\x018=FIX.4.4\x019=',
        b'113\x0135=A\x0149=sndrcompid\x0156=tgtcompid\x0134=1\x0152=20160331-15:52:08.508\x0198=0\x01108=2\x01141=',
        b'Y\x01553=sndrcompid\x01554=$ecretP4ssword\x0110=110\x01',
    ]

    fix_tags = [
        b'8=FIX.4.4',
        b'9=113',
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

    output = [
        fix_tags[:3],
        fix_tags[:5],
        fix_tags[:9],
        fix_tags[:12],
        fix_tags + fix_tags[:1],
        fix_tags + fix_tags[:9],
        fix_tags + fix_tags[:13],
        ]

    def test_tagRecieved(self):

        t = proto_helpers.StringIOWithoutClosing()
        a = FixTagReceiverTester()
        a.makeConnection(protocol.FileWrapper(t))
        for i in range(0, len(self.fix_buffers)):
            a.dataReceived(self.fix_buffers[i])

            self.assertEqual(self.output[i], a.tags)


class LongTagLengthTester(FixTagReceiver):

    MAX_TAG_LENGTH=20
    longTags = list()

    def tagLengthExceeded(self, tag):
        self.longTags.append(tag)

    def tagReceived(self, tag):
        '''
        This has to be implemented
        '''
        pass

class LongTagLengthTests(TestCase):

    fix_buffers = [
        b'8=FIX.4.4\x019=115\x0135=A\x0149=this_is_a_really_long_tag\x0156=tcid\x01'
    ]

    fix_tags = [
        b'49=this_is_a_really_long_tag\x0156=tcid\x01',
    ]

    output = [
        fix_tags[:3],
        fix_tags[:5],
        fix_tags[:9],
        fix_tags[:12],
        fix_tags + fix_tags[:1],
        fix_tags + fix_tags[:9],
        fix_tags + fix_tags[:13],
        ]

    def test_LongTag(self):

        t = proto_helpers.StringIOWithoutClosing()
        a = LongTagLengthTester()
        a.makeConnection(protocol.FileWrapper(t))
        for i in range(0, len(self.fix_buffers)):
            a.dataReceived(self.fix_buffers[i])
            self.assertEqual(self.output[i], a.longTags)





