=================
Writting a Client
=================

PokerTHProto is built with `Twisted <https://twistedmatrix.com/>`__, an
event-driven networking engine engine written in Python. That means it is rather
useful to have basic knowledge about `event-driven programming
<http://en.wikipedia.org/wiki/Event-driven_programming>`_. But don't get
scared, it is pretty easy.


Twisted Application
===================

The easiest way to write a PokerTH client is to write an `Twisted application
<http://twistedmatrix.com/documents/current/core/howto/application.html>`__.

This basic ``my_client.tac`` file gives you an idea::

    from twisted.application import internet, service
    from twisted.internet import reactor

    from pokerthproto.protocol import ClientProtocolFactory, ClientProtocol
    from pokerthproto.lobby import GameInfo, LobbyError
    from pokerthproto.poker import Action


    class PyClientProtocol(ClientProtocol):
        def handleInsideLobby(self, lobbyInfo):
            try:
                gameId = self.factory.lobby.getGameInfoId('My Online Game')
            except LobbyError:
                reactor.callLater(1, self.handleInsideLobby, lobbyInfo)
            else:
                self.sendJoinExistingGame(gameId)

        def handleMyTurn(self, gameInfo):
            if gameInfo.highestSet > gameInfo.myBet:
                action, bet = Action.CALL, gameInfo.highestSet
            else:
                action = Action.CHECK
            self.sendMyAction(action, gameInfo.highestSet - gameInfo.myBet)


    class PyClientProtocolFactory(ClientProtocolFactory):
        protocol = PyClientProtocol


    application = service.Application('PokerTH Client')
    client_factory = PyClientProtocolFactory('PyClient1')
    service = internet.TCPClient('localhost', 7234, client_factory)
    service.setServiceParent(application)

Here, we create an own protocol by inhereting from ``ClientProtocol`` and
overwritting some methods in order to adapt them to our needs. For instance,
the ``handleInsideLobby`` method is triggered when we are inside the lobby.
In this case, our action is to join the game named *My Online Game* if available
otherwise we wait one second and try again. The method ``handleMyTurn`` is called
during a poker game and here we specified that we want to check if possible and
otherwise call.
The remaining lines are just boilerplate code to define a Twisted application.
You can run this client by calling::

    twisted -y my_client.tac -n


Mandatory Methods
=================

Your own protocol needs to define some mandatory methods:

* :obj:`~.handleInsideLobby`: This method is called when we are inside the lobby.
  Use :obj:`~.sendJoinExistingGame` or :obj:`~.sendJoinNewGame` to
  join or create a new game. If you create a new game use :obj:`~.sendStartEvent`
  to start the game. The ``lobbyInfo`` argument of type :obj:`~.Lobby` provides
  you information about other players and games.

* :obj:`~.handleMyTurn`: This method is called when our turn starts. Use
  :obj:`~.sendMyAction` to decide what action you want to take. The current
  state of the game is represented with the ``gameInfo`` parameter of type
  :obj:`~.Game` in both functions.


Optional Methods
================

* :obj:`~.handleChat`: This method is called when a chat message was received.
  Use :obj:`~.sendChatRequest` to reply or start a chat.

* :obj:`~.handleOthersTurn`: This method is called when another player starts
  its turn. You could use this event to chat him up.
