# -*- coding: utf-8 -*-
"""
The PokerTH protocol consisting of messages and replies with respect to the
current state in the communication.
"""
from __future__ import print_function, absolute_import, division

from twisted.internet import reactor
from twisted.python import log
from twisted.internet.protocol import Protocol, ClientFactory

from . import pokerth_pb2
from . import transport
from . import lobby
from . import game
from . import poker

__author__ = 'Florian Wilhelm'
__copyright__ = 'Florian Wilhelm'


class PokerTHProtocol(Protocol):
    _buffer = ''
    _msgSize = None

    def _getBufferedData(self, data):
        self._buffer += data
        bufData = []
        while True:
            if self._msgSize is None:
                if len(self._buffer) >= 4:
                    self._msgSize = transport.readSizeBytes(self._buffer[:4])
                    self._buffer = self._buffer[4:]
                else:
                    break
            if len(self._buffer) >= self._msgSize:
                bufData.append(self._buffer[:self._msgSize])
                self._buffer = self._buffer[self._msgSize:]
                self._msgSize = None
            else:
                break
        return bufData

    @staticmethod
    def _getHook(msg_name):
        hook = msg_name.replace('Message', 'Received')
        return hook[0].lower() + hook[1:]

    def unhandledMessageReceived(self, msg):
        log.msg('Received unhandled message {}:\n{}'.format(
            msg.__class__.__name__, msg))

    def connectionMade(self):
        log.msg('Connection established.')

    def dataReceived(self, data):
        for buffer in self._getBufferedData(data):
            msg = transport.develop(transport.unpack(buffer))
            msg_name = msg.__class__.__name__
            hook = self._getHook(msg_name)
            #log.msg("Data: {}".format(buffer.encode('hex')))
            log.msg("{} received".format(msg_name))
            #log.msg(msg, logLevel=logging.DEBUG)
            getattr(self, hook)(msg)

    def _sendMessage(self, msg):
        envelope = transport.envelop(msg)
        self.transport.write(transport.pack(envelope))

    def connectionLost(self, reason):
        log.msg('Connection lost due to: {}'.format(reason))


# Set default method for all possible message types
for msg_type in pokerth_pb2.PokerTHMessage.PokerTHMessageType.keys():
    msg_name = msg_type.split("_", 1)[1]
    hook = PokerTHProtocol._getHook(msg_name)
    setattr(PokerTHProtocol, hook, PokerTHProtocol.unhandledMessageReceived)


class States(object):
    """
    Enum of all client states
    """
    INIT = 0
    LOBBY = 1
    GAME_JOINED = 2
    GAME_STARTED = 3


class ClientProtocol(PokerTHProtocol):
    state = States.INIT

    def announceReceived(self, msg):
        reply = pokerth_pb2.InitMessage()

        replyVersion = reply.requestedVersion
        msgVersion = msg.protocolVersion
        replyVersion.majorVersion = msgVersion.majorVersion
        replyVersion.minorVersion = msgVersion.minorVersion

        reply.buildId = 0  # 0 for Linux build
        reply.nickName = self.factory.nickName
        if msg.serverType == msg.serverTypeInternetNoAuth:
            reply.login = reply.unauthenticatedLogin
        else:
            raise NotImplementedError("Handle authentication!")
        assert reply.IsInitialized()
        self._sendMessage(reply)
        log.msg("InitMessage sent")

    def initAckReceived(self, msg):
        self.factory.playerId = msg.yourPlayerId
        self.factory.sessionId = msg.yourSessionId
        self.state = States.LOBBY
        reactor.callLater(1, self.handleInsideLobby, self.factory.lobby)

    def handleInsideLobby(self, lobbyInfo):
        """
        Handle the behavior of our client in the lobby.

        Overwrite this method.

        :param lobbyInfo: information about the lobby (:obj:`~.Lobby`)
        """
        raise NotImplementedError("We are in the lobby, implement an action!")

    def sendJoinExistingGame(self, gameId, autoLeave=False):
        msg = pokerth_pb2.JoinExistingGameMessage()
        msg.gameId = gameId
        msg.autoLeave = autoLeave
        self._sendMessage(msg)
        log.msg("JoinExistingGameMessage sent")

    def sendJoinNewGame(self, gameInfo, password=None, autoLeave=False):
        msg = pokerth_pb2.JoinNewGameMessage()
        msg.gameInfo.MergeFrom(gameInfo.getMsg())
        if password is not None:
            msg.password = password
        msg.autoLeave = autoLeave
        self._sendMessage(msg)
        log.msg("JoinNewGameMessage sent")

    def playerListReceived(self, msg):
        if msg.playerListNotification == msg.playerListNew:
            self.factory.lobby.addPlayer(msg.playerId)
            reply = pokerth_pb2.PlayerInfoRequestMessage()
            reply.playerId.append(msg.playerId)
            self._sendMessage(reply)
            log.msg("InfoRequestMessage sent")
        else:  # msg.playerListLeft
            self.factory.lobby.delPlayer(msg.playerId)

    def playerInfoReplyReceived(self, msg):
        self.factory.lobby.setPlayerInfo(msg.playerId, msg.playerInfoData)

    def gameListNewReceived(self, msg):
        gameInfo = lobby.GameInfo()
        gameInfo.setInfo(msg.gameInfo)
        gameInfo.gameId = msg.gameId
        gameInfo.gameMode = msg.gameMode
        gameInfo.isPrivae = msg.isPrivate
        gameInfo.adminPlayerId = msg.adminPlayerId
        self.factory.lobby.addGameInfo(gameInfo)

    def gameListPlayerJoinedReceived(self, msg):
        self.factory.lobby.addPlayerToGame(msg.playerId, msg.gameId)

    def gameListPlayerLeftReceived(self, msg):
        self.factory.lobby.delPlayerFromGame(msg.playerId, msg.gameId)

    def gamePlayerJoinedReceived(self, msg):
        game = self.factory.game
        assert game.gameId == msg.gameId
        player = self.factory.lobby.getPlayer(msg.playerId)
        game.addPlayer(player)

    def gamePlayerLeftReceived(self, msg):
        game = self.factory.game
        assert game.gameId == msg.gameId
        player = self.factory.lobby.getPlayer(msg.playerId)
        # TODO: Handle GamePlayerLeftReason
        game.delPlayer(player)

    def joinGameAckReceived(self, msg):
        self.factory.game = game.Game(msg.gameId, self.factory.playerId)
        if msg.areYouGameAdmin:
            myGameInfo = self.factory.lobby.getGameInfo(msg.gameId)
            assert myGameInfo.adminPlayerId == self.factory.playerId
        myself = self.factory.lobby.getPlayer(self.factory.playerId)
        self.factory.game.addPlayer(myself)
        self.state = States.GAME_JOINED

    def gameListUpdateReceived(self, msg):
        gameInfo = self.factory.lobby.getGameInfo(msg.gameId)
        gameInfo.gameMode = msg.gameMode

    def sendStartEvent(self, gameId, startEventType=None, fillWithBots=False):
        msg = pokerth_pb2.StartEventMessage()
        msg.gameId = gameId
        if startEventType is not None:
            msg.startEventType = startEventType
        msg.fillWithComputerPlayers = fillWithBots
        self._sendMessage(msg)
        log.msg("StartEventMessage sent")

    def startEventReceived(self, msg):
        assert self.factory.game.gameId == msg.gameId
        gameInfo = self.factory.lobby.getGameInfo(msg.gameId)
        gameInfo.fillWithComputerPlayers = msg.fillWithComputerPlayers
        reply = pokerth_pb2.StartEventAckMessage()
        reply.gameId = msg.gameId
        self._sendMessage(reply)
        log.msg("StartEventAckMessage sent")
        self.state = States.GAME_STARTED

    def chatReceived(self, msg):
        chatType = enum2str(pokerth_pb2.ChatMessage.ChatType, msg.chatType)
        chatType = chatType.replace('chatType', '')
        lobby = self.factory.lobby
        if msg.gameId != 0:
            game = self.factory.game
            assert game.gameId == msg.gameId
        else:
            game = None
        if msg.playerId != 0:
            player = lobby.getPlayer(msg.playerId)
        else:
            player = None
        self.handleChat(chatType, msg.chatText, lobby, game, player)

    def sendChatRequest(self, text, gameId=None, playerId=None):
        """
        Send a chat message.

        :param text: your message
        :param gameId: optional game id
        :param playerId: optional player id
        """
        msg = pokerth_pb2.ChatRequestMessage()
        msg.chatText = text
        if gameId is not None:
            msg.targetGameId = gameId
        if playerId is not None:
            msg.targetPlayerId = playerId
        self._sendMessage(msg)
        log.msg("ChatRequestMessage sent")

    def handleChat(self, chatType, text, lobbyInfo, gameInfo=None,
                   playerInfo=None):
        """
        Handle the behavior of our client when a chat message was received.

        Overwrite this method.

        :param chatType: "Lobby", "Game", "Bot", "Broadcast" or "Private"
        :param text: text of the message
        :param lobbyInfo: lobby information (:obj:`~.Lobby`)
        :param gameInfo: optional game information (:obj:`~.Game`)
        :param playerInfo: optional player information (:obj:`~.Player`)
        """
        log_str = ''
        if gameInfo is not None:
            log_str += '<{game}> '
            gameInfo = lobbyInfo.getGameInfo(gameInfo.gameId).gameName
        if playerInfo is not None:
            log_str += '{player} '
            playerInfo = playerInfo.name
        log_str += '[{type}]: {text}'
        log.msg(log_str.format(game=gameInfo, player=playerInfo,
                               type=chatType, text=text))

    def gameStartInitialReceived(self, msg):
        game = self.factory.game
        assert game.gameId == msg.gameId
        game.dealer = game.getPlayer(msg.startDealerPlayerId)
        for seat, playerId in enumerate(msg.playerSeats):
            player = game.getPlayer(playerId)
            player.seat = seat

    def handStartReceived(self, msg):
        game = self.factory.game
        assert game.gameId == msg.gameId
        game.startNewHand()
        game.smallBlind = msg.smallBlind
        cards = (msg.plainCards.plainCard1, msg.plainCards.plainCard2)
        game.pocketCards = [poker.intToCard(card) for card in cards]
        # TODO: Handle Seatstates
        log.msg("Got cards {}".format(game.pocketCards))

    def playersActionDoneReceived(self, msg):
        game = self.factory.game
        assert game.gameId == msg.gameId
        round = msg.gameState
        if round != game.currRound and round in poker.poker_rounds[:2]:
            game.addRound(round)
        game.addAction(msg.playerId, msg.playerAction, msg.totalPlayerBet)
        game.highestSet = msg.highestSet
        game.minimumRaise = msg.minimumRaise
        player = game.getPlayer(msg.playerId)
        player.money = msg.playerMoney

    def playersTurnReceived(self, msg):
        game = self.factory.game
        assert game.gameId == msg.gameId
        # First real turn of a player triggers Preflop
        if game.currRound in poker.poker_rounds[:2]:
            game.addRound(poker.Round.PREFLOP)
        if msg.playerId == self.factory.playerId:
            self.handleMyTurn(game)
        else:
            player = self.factory.lobby.getPlayer(msg.playerId)
            self.handleOthersTurn(player, game)

    def sendMyAction(self, action, bet, relative=True):
        """
        Send my action during a poker game.

        :param action: action of :obj:`~.poker.Action`
        :param bet: bet with respect to the action
        :param relative: boolean if the bet is relative to the highest set bet
        """
        game = self.factory.game
        msg = pokerth_pb2.MyActionRequestMessage()
        msg.myAction = action
        if not relative:
            bet -= game.highestSet
        msg.myRelativeBet = bet
        msg.gameId = game.gameId
        msg.handNum = game.handNum
        msg.gameState = game.currRound
        self._sendMessage(msg)

    def yourActionRejected(self, msg):
        raise RuntimeError("Wrong action taken:\n{}".format(msg))

    def handleOthersTurn(self, playerInfo, gameInfo):
        """
        Handle the start of another player's turn.

        :param playerInfo: player information (:obj:`~.Player`)
        :param gameInfo: game information (:obj:`~.Game`)
        """
        log.msg("Turn of player {}".format(playerInfo.name))

    def handleMyTurn(self, gameInfo):
        """
        Decide what action to take when it is our turn.

        :param gameInfo: game information (:obj:`~.Game`)
        """
        raise NotImplementedError("What action should I take?")

    def dealFlopCardsReceived(self, msg):
        game = self.factory.game
        assert game.gameId == msg.gameId
        assert game.currRound == poker.Round.PREFLOP
        card1 = poker.intToCard(msg.flopCard1)
        card2 = poker.intToCard(msg.flopCard2)
        card3 = poker.intToCard(msg.flopCard3)
        game.addRound(poker.Round.FLOP, cards=[card1, card2, card3])
        game.highestSet = 0

    def dealTurnCardReceived(self, msg):
        game = self.factory.game
        assert game.gameId == msg.gameId
        assert game.currRound == poker.Round.FLOP
        card = poker.intToCard(msg.turnCard)
        game.addRound(poker.Round.TURN, cards=[card])
        game.highestSet = 0

    def dealRiverCardReceived(self, msg):
        game = self.factory.game
        assert game.gameId == msg.gameId
        assert game.currRound == poker.Round.TURN
        card = poker.intToCard(msg.riverCard)
        game.addRound(poker.Round.RIVER, cards=[card])
        game.highestSet = 0

    def allInShowCardsReceived(self, msg):
        game = self.factory.game
        assert game.gameId == msg.gameId
        for playerAllin in msg.playersAllIn:
            card1 = poker.intToCard(playerAllin.allInCard1)
            card2 = poker.intToCard(playerAllin.allInCard2)
            game.addOthersCards(playerAllin.playerId, [card1, card2])

    def _recordResult(self, result):
        game = self.factory.game
        game.addWin(result.playerId, result.moneyWon)
        card1 = poker.intToCard(result.resultCard1)
        card2 = poker.intToCard(result.resultCard2)
        game.addOthersCards(result.playerId, [card1, card2])
        player = game.getPlayer(result.playerId)
        player.money = result.playerMoney

    def endOfHandShowCardsReceived(self, msg):
        game = self.factory.game
        assert game.gameId == msg.gameId
        for result in msg.playerResults:
            self._recordResult(result)
        self.handleEndOfHand(game)

    def endOfHandHideCardsReceived(self, msg):
        game = self.factory.game
        assert game.gameId == msg.gameId
        game.addWin(msg.playerId, msg.moneyWon)
        player = game.getPlayer(msg.playerId)
        player.money = msg.playerMoney
        self.handleEndOfHand(game)

    def showMyCardsRequestReceived(self, msg):
        pass  # empty message

    def afterHandShowCardsReceived(self, msg):
        game = self.factory.game
        assert game.gameId == msg.gameId
        self._recordResult(msg.playerResult)
        self.handleEndOfHand(game)

    def handleEndOfHand(self, gameInfo):
        """
        Handle the end of a hand

        :param gameInfo: game information (:obj:`~.Game`)
        """
        log.msg("End of hand {}".format(gameInfo.handNum))

    def endOfGameReceived(self, msg):
        game = self.factory.game
        assert game.gameId == msg.gameId
        winner = game.getPlayer(msg.winnerPlayerId)
        self.state = States.GAME_JOINED
        reactor.callLater(1, self.handleEndOfGame, game, winner)

    def handleEndOfGame(self, gameInfo, winner):
        """
        Handle the end of a game

        The end of a game brings you back to the lobby

        :param gameInfo: game information (:obj:`~.Game`)
        :param winner: winner of the game (:obj:`~.Player`)
        """
        log.msg("End of game {}\n"
                "Winner: {}".format(gameInfo.handNum,
                                    winner.name))


class ClientProtocolFactory(ClientFactory):
    protocol = ClientProtocol

    def __init__(self, nickName):
        self.nickName = nickName
        self.playerId = None
        self.SessionID = None
        self.game = None
        self.lobby = lobby.Lobby()

    def clientConnectionLost(self, connector, reason):
        pass
        #connector.connect()

    def clientConnectionFailed(self, connector, reason):
        reactor.stop()


def enum2str(enumType, enum):
    """
    Translates a pokerth_pb2 enum type to a string.

    :param enumType: enum type class
    :param enum: the enum element of the type
    :return: identifier string of enum
    """
    return [k for k, v in enumType.items() if v == enum][0]
