# -*- coding: utf-8 -*-

from __future__ import print_function, absolute_import, division

import random

from twisted.internet.endpoints import TCP4ServerEndpoint, connectProtocol, \
    TCP4ClientEndpoint
from twisted.internet import reactor
from twisted.internet.defer import Deferred

from .fixtures import pokerth_server

from pokerthproto import proxy
from pokerthproto import protocol
from pokerthproto.protocol import ClientProtocol, ClientProtocolFactory

__author__ = 'Florian Wilhelm'
__copyright__ = 'Florian Wilhelm'


def test_ProxyProtocol(pokerth_server):
    class PyClientProtocol(ClientProtocol):

        def handleInsideLobby(self, lobbyInfo):
            pass

    class PyClientProtocolFactory(ClientProtocolFactory):
        protocol = PyClientProtocol

    def test_state(proto):
        assert proto.state == protocol.States.LOBBY

    def start_client(proto):
        client_endpoint = TCP4ClientEndpoint(reactor, 'localhost', 1234)
        nickname = 'PyClient' + str(random.getrandbits(23))
        factory = PyClientProtocolFactory(nickname)
        proto = factory.buildProtocol(('localhost', 0))
        connectProtocol(client_endpoint, proto)
        d = Deferred()
        reactor.callLater(4, d.callback, proto)
        d.addCallback(test_state)
        return d

    server_endpoint = TCP4ServerEndpoint(reactor, 1234)
    d = server_endpoint.listen(proxy.ProxyProtocolFactory())
    d.addCallback(start_client)
    return d
