# -*- coding: utf-8 -*-

from __future__ import print_function, absolute_import, division

import pytest

from pokerthproto.pokerth_pb2 import PokerTHMessage

__author__ = 'Florian Wilhelm'
__copyright__ = 'Florian Wilhelm'


@pytest.fixture
def initMsgData():
    return b'\x00\x00\x00\x1c\x08\x02\x1a\x18\n\x04\x08\x05\x10\x01' \
        '\x10\x00(\x022\x0cHuman Player'


@pytest.fixture
def initMsg():
    msg = PokerTHMessage()
    msg.ParseFromString(initMsgData()[4:])
    return msg
