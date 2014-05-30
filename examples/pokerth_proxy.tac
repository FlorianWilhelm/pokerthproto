# -*- coding: utf-8 -*-

from __future__ import print_function, absolute_import
from twisted.application import internet, service

from pokerthproto.proxy import ProxyProtocolFactory

__author__ = 'Florian Wilhelm'
__copyright__ = 'Florian Wilhelm'

application = service.Application('PokerTH Proxy Server')
proxyService = internet.TCPServer(1234, ProxyProtocolFactory())
proxyService.setServiceParent(application)
