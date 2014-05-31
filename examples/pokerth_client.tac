# -*- coding: utf-8 -*-

from __future__ import print_function, absolute_import, division
from twisted.application import internet, service

from pokerthproto.protocol import ClientProtocolFactory

__author__ = 'Florian Wilhelm'
__copyright__ = 'Florian Wilhelm'

application = service.Application('PokerTH Client')
client_factory = ClientProtocolFactory('PyClient')
service = internet.TCPClient('localhost', 7234, client_factory)
service.setServiceParent(application)
