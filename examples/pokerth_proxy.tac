# -*- coding: utf-8 -*-

from __future__ import print_function, absolute_import, division
from twisted.application import internet, service

from pokerthproto.proxy import ProxyProtocolFactory

__author__ = 'Florian Wilhelm'
__copyright__ = 'Florian Wilhelm'

application = service.Application('PokerTH Proxy Server')
service = internet.TCPServer(1234, ProxyProtocolFactory())
service.setServiceParent(application)
