from twisted.application import internet, service
from twisted.internet import reactor

from pokerthproto.protocol import ClientProtocolFactory, ClientProtocol
from pokerthproto.lobby import GameInfo, LobbyError
from pokerthproto.poker import Action

class PyClientProtocol(ClientProtocol):
    def handleInsideLobby(self, lobby):
        try:
            gameId = self.factory.lobby.getGameInfoId('My Online Game')
        except LobbyError:
            reactor.callLater(1, self.handleInsideLobby, lobby)
        else:
            self.sendJoinExistingGame(gameId)

    def handleMyTurn(self, game):
        if game.highestSet > game.myBet:
            action, bet = Action.CALL, game.highestSet
        else:
            action = Action.CHECK
        self.sendMyAction(action, game.highestSet - game.myBet)


class PyClientProtocolFactory(ClientProtocolFactory):
    protocol = PyClientProtocol

application = service.Application('PokerTH Client')
client_factory = PyClientProtocolFactory('PyClient1')
service = internet.TCPClient('localhost', 7234, client_factory)
service.setServiceParent(application)