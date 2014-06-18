# -*- coding: utf-8 -*-

from __future__ import print_function, absolute_import, division
from twisted.application import internet, service

from twisted.internet import reactor
from pokerthproto.protocol import ClientProtocolFactory, ClientProtocol
from pokerthproto.lobby import GameInfo, LobbyError

__author__ = 'Florian Wilhelm'
__copyright__ = 'Florian Wilhelm'


class PyClientProtocol(ClientProtocol):
    def insideLobby(self):
        self.joinGame('My Online Game')

    def joinGame(self, gameName):
        try:
            gameId = self.factory.lobby.getGameInfoId(gameName)
        except LobbyError:
            reactor.callLater(1, self.joinGame, gameName)
        else:
            self.sendJoinExistingGameMessage(gameId)

    def createGame(self):
        gameInfo = GameInfo('PyClient Game')
        self.sendJoinNewGameMessage(gameInfo)


class PyClientProtocolFactory(ClientProtocolFactory):
    protocol = PyClientProtocol



application = service.Application('PokerTH Client')
client_factory = PyClientProtocolFactory('PyClient1')
service = internet.TCPClient('localhost', 7234, client_factory)
service.setServiceParent(application)
