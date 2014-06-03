# -*- coding: utf-8 -*-

from __future__ import print_function, absolute_import

import random

from twisted.internet.endpoints import TCP4ClientEndpoint, connectProtocol
from twisted.internet import reactor
from twisted.internet.defer import Deferred

from .fixtures import pokerth_server

from pokerthproto import protocol

__author__ = 'Florian Wilhelm'
__copyright__ = 'Florian Wilhelm'


def test_ClientProtocol(pokerth_server):
    def test_state(proto):
        assert proto.state == protocol.States.LOBBY

    endpoint = TCP4ClientEndpoint(reactor, 'localhost', 7234)
    nickname = 'PyClient' + str(random.getrandbits(16))
    factory = protocol.ClientProtocolFactory(nickname)
    proto = factory.buildProtocol(('localhost', 7234))
    connectProtocol(endpoint, proto)
    d = Deferred()
    reactor.callLater(2, d.callback, proto)
    d.addCallback(test_state)
    return d
