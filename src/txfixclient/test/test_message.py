from twisted.trial.unittest import TestCase
from txfixclient.message import FixMessage


class FixMessageTests(TestCase):

    def setUp(self):
        self.msg = FixMessage()

    def test_new_fix_message(self):
        self.assertEqual(self.msg.length, 0)
        self.assertEqual(self.msg.checksum, None)
        self.assertEqual(self.msg.type, None)
        self.assertEqual(self.msg._complete, False)

    def test_append_tag(self):
        self.msg.append_tag(35, 'A')
        self.assertEqual(self.msg._data, [(35, 'A'), ])

    def test_setup(self):
        self.assertEqual(self.msg._data, [])

    def test_append_tags(self):
        tags_a = [
            (8, 'FIX.4.4'),
            (9, '116'),
            (35, 'A'),
            (49, 'sender_compid'),
            (56, 'target_compid'),
        ]
        tags_b = [
            (34, '1'),
            (52, '20160407-13:26:32.398'),
            (98, '0'),
            (108, '30'),
            (141, 'Y'),
            (553, 'username'),
            (554, '$ecretP4ass'),
        ]
        self.msg.append_tags(tags_a)
        self.msg.append_tags(tags_b)
        self.assertEqual(self.msg._data, tags_a + tags_b)

    def test_tag_to_string(self):

        tags = [
            (8, 'FIX.4.4'),
            (9, '116'),
            (35, 'A'),
            (49, 'sender_compid'),
            (56, 'target_compid'),
            (34, '1'),
            (52, '20160407-13:26:32.398'),
            (98, '0'),
            (108, '30'),
            (141, 'Y'),
            (553, 'username'),
            (554, '$ecretP4ass'),
        ]
        results = [
            b'8=FIX.4.4\x01',
            b'9=116\x01',
            b'35=A\x01',
            b'49=sender_compid\x01',
            b'56=target_compid\x01',
            b'34=1\x01',
            b'52=20160407-13:26:32.398\x01',
            b'98=0\x01',
            b'108=30\x01',
            b'141=Y\x01',
            b'553=username\x01',
            b'554=$ecretP4ass\x01',
        ]
        for i in range(0, len(tags)):
            self.assertEqual(self.msg._tag_to_string(tags[i][0], tags[i][1]), results[i])

        self.assertEqual(self.msg._tag_to_string(8, 'FIX.4.4'), b'8=FIX.4.4\x01')


    def test_as_binary_and_string(self):

        tags = [
            (8, 'FIX.4.4'),
            (9, '116'),
            (35, 'A'),
            (49, 'sender_compid'),
            (56, 'target_compid'),
            (34, '1'),
            (52, '20160407-13:26:32.398'),
            (98, '0'),
            (108, '30'),
            (141, 'Y'),
            (553, 'username'),
            (554, '$ecretP4ass'),
        ]
        results = b'8=FIX.4.4\x019=116\x0135=A\x0149=sender_compid\x0156=target_compid\x0134=1\x0152=20160407-13:26:32.398\x0198=0\x01108=30\x01141=Y\x01553=username\x01554=$ecretP4ass\x0110=059\x01'
        self.msg.append_tags(tags)
        self.assertEqual(self.msg.as_binary(), results)
        self.assertEqual(self.msg.as_string(), results.replace(b'\x01', b'|'))

    def test_get_tag(self):
        tags = [
            (8, 'FIX.4.4'),
            (9, '116'),
            (35, 'A'),
            (49, 'sender_compid'),
            (56, 'target_compid'),
            (34, '1'),
            (52, '20160407-13:26:32.398'),
            (98, '0'),
            (108, '30'),
            (141, 'Y'),
            (553, 'username'),
            (554, '$ecretP4ass'),
        ]
        self.msg.append_tags(tags)
        self.assertEqual(self.msg.get_tag(52), [(52, b'20160407-13:26:32.398')])


