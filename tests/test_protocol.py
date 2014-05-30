# -*- coding: utf-8 -*-

from __future__ import print_function, absolute_import

from twisted.trial import unittest
from twisted.test import proto_helpers

from pokerthproto import pokerth_pb2
from IPython import embed

__author__ = 'Florian Wilhelm'
__copyright__ = 'Florian Wilhelm'


def test_pokerth_pb2():
    with open("dump_login") as fh:
        content = fh.read()
    msg = pokerth_pb2.PokerTHMessage()
    msg.ParseFromString(content)
    embed()
