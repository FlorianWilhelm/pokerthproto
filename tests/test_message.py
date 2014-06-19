# -*- coding: utf-8 -*-

from __future__ import print_function, absolute_import, division

__author__ = 'Florian Wilhelm'
__copyright__ = 'Florian Wilhelm'

from pokerthproto import message
from pokerthproto.pokerth_pb2 import PokerTHMessage

from .fixtures import initMsg, initMsgData


def test_develop(initMsg):
    msg = message.develop(initMsg)
    assert hasattr(msg, 'nickName')


def test_envelop(initMsg):
    init_msg = initMsg.initMessage
    envelope = message.envelop(init_msg)
    assert envelope.IsInitialized()
    assert envelope.messageType == envelope.Type_InitMessage
    assert envelope.initMessage.IsInitialized()


def test_make_read_SizeBytes():
    for i in [1, 10, 11, 15, 16, 32, 33, 63, 64, 1000, 10000]:
        size_bytes = message.makeSizeBytes(i)
        assert len(size_bytes) == 4
        n = message.readSizeBytes(size_bytes)
        assert i == n


def test_pack_unpack(initMsgData):
    envelope = message.unpack(initMsgData[4:])
    assert isinstance(envelope, PokerTHMessage)
    data = message.pack(envelope)
    assert data == initMsgData
