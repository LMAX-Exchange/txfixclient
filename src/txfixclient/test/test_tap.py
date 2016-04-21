# -*- coding: utf-8 -*-
# vim:fenc=utf-8

from twisted.trial import unittest
from txfixclient import tap


class FixclientTapTests(unittest.TestCase):

    def test_options(self):
        opt = tap.Options()
        opt.parseOptions(['--hostname', 'myhost'])
        opt.parseOptions(['--port', 8443])
        opt.parseOptions(['--spec', 'foo'])
        self.assertEqual(opt['hostname'], 'myhost')
        self.assertEqual(opt['port'], '8443')

