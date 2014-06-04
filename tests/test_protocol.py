# -*- coding: utf-8 -*-

from __future__ import print_function, absolute_import

import sys
import random

from twisted.internet.endpoints import TCP4ClientEndpoint, connectProtocol
from twisted.internet import reactor
from twisted.python import log
from twisted.internet.defer import Deferred

from .fixtures import pokerth_server

from pokerthproto import protocol

__author__ = 'Florian Wilhelm'
__copyright__ = 'Florian Wilhelm'

log.startLogging(sys.stdout)


def test_lobby(pokerth_server):
    def test_state(proto):
        assert proto.state == protocol.States.LOBBY
        return proto

    endpoint = TCP4ClientEndpoint(reactor, 'localhost', 7234)
    nickname = 'PyClient' + str(random.getrandbits(23))
    factory = protocol.ClientProtocolFactory(nickname)
    proto = factory.buildProtocol(('localhost', 0))
    connectProtocol(endpoint, proto)
    d = Deferred()
    reactor.callLater(1, d.callback, proto)
    d.addCallback(test_state)
    return d


def test_players(pokerth_server):
    def test_players(factory):
        assert factory.players[0].name == nickname
        return proto

    endpoint = TCP4ClientEndpoint(reactor, 'localhost', 7234)
    nickname = 'PyClient' + str(random.getrandbits(23))
    factory = protocol.ClientProtocolFactory(nickname)
    proto = factory.buildProtocol(('localhost', 0))
    connectProtocol(endpoint, proto)
    d = Deferred()
    reactor.callLater(1, d.callback, factory)
    d.addCallback(test_players)
    return d
