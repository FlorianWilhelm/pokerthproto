# -*- coding: utf-8 -*-

from __future__ import print_function, absolute_import

import sys

from twisted.internet.endpoints import TCP4ClientEndpoint, connectProtocol
from twisted.internet import reactor
from twisted.python import log

from .fixtures import pokerth_server

from pokerthproto import protocol

__author__ = 'Florian Wilhelm'
__copyright__ = 'Florian Wilhelm'


def test_ClientProtocol(pokerth_server):
    log.startLogging(sys.stdout)
    endpoint = TCP4ClientEndpoint(reactor, 'localhost', 7234)
    factory = protocol.ClientProtocolFactory('PyClient')
    proto = factory.buildProtocol('localhost')
    d = connectProtocol(endpoint, proto)
    return d


log.startLogging(sys.stdout)
endpoint = TCP4ClientEndpoint(reactor, 'localhost', 7234)
endpoint.connect(protocol.ClientProtocolFactory('PyClient'))