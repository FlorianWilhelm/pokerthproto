# -*- coding: utf-8 -*-
"""
All functionality related to a poker game and its representation.
"""

from __future__ import print_function, absolute_import, division

from .poker import poker_rounds, Round, Action, deck

__author__ = 'Florian Wilhelm'
__copyright__ = 'Florian Wilhelm'


class ActionInfo(object):
    """
    The action of a player during the poker game.

    :param player: player (:obj:`~.Player`)
    :param kind: type of the action (:obj:`~.Action`)
    :param money: stake of the action if available
    """

    def __init__(self, player, kind, money=None):
        self.player = player
        self.kind = kind
        self.money = money

    def __eq__(self, other):
        if isinstance(other, ActionInfo):
            return self.__dict__ == other.__dict__
        return NotImplemented

    def __unicode__(self):
        content = "Player: {}, kind: {}, money: {}".format(self.player,
                                                           self.kind,
                                                           self.money)
        return unicode(content)

    def __str__(self):
        return unicode(self).encode('utf-8')


class RoundInfo(object):
    """
    Information about the poker round.

    :param gameState: name of the poker round (:obj:`~.Round`)
    :param cards: board card of the round as defined in :obj:`~.deck`
    """

    def __init__(self, gameState, cards=None):
        assert gameState in poker_rounds
        self._gameState = gameState
        self._cards = cards if cards else []
        self._actions = []

    @property
    def actions(self):
        return self._actions

    @property
    def gameState(self):
        return self._gameState

    @property
    def name(self):
        for attr, value in vars(Round).items():
            if attr.startswith("__"):
                continue
            if value == self._gameState:
                return attr

    @property
    def cards(self):
        return self._cards

    def __eq__(self, other):
        if isinstance(other, RoundInfo):
            return self.__dict__ == other.__dict__
        return NotImplemented

    def __unicode__(self):
        content = {'GameState': self._gameState,
                   'Cards': self._cards,
                   'Actions': str(self._actions)}
        return unicode(content)

    def __str__(self):
        return unicode(self).encode('utf-8')


class GameError(Exception):

    def __unicode__(self):
        return unicode(self.message)

    def __str__(self):
        return unicode(self).encode('utf-8')


class Game(object):
    """
    A poker game holding the information about the actions of the players.
    """
    def __init__(self, gameId, myPlayerId):
        self._gameId = gameId
        self._myPlayerId = myPlayerId
        self._players = []
        self._dealer = None
        self._rounds = []
        self._pocketCards = None
        self._boardCards = []
        self._smallBlind = None
        self._highestSet = 0
        self._minimumRaise = 0
        self._handNum = 1

    @property
    def seats(self):
        seats = sorted([(p.seat, p) for p in self.players])
        return [p for _, p in seats]

    @property
    def handNum(self):
        return self._handNum

    @property
    def minimumRaise(self):
        return self._minimumRaise

    @minimumRaise.setter
    def minimumRaise(self, money):
        self._minimumRaise = money

    @property
    def highestSet(self):
        return self._highestSet

    @highestSet.setter
    def highestSet(self, money):
        self._highestSet = money

    @property
    def smallBlind(self):
        return self._smallBlind

    @smallBlind.setter
    def smallBlind(self, money):
        self._smallBlind = money

    @property
    def bigBlind(self):
        return 2*self._smallBlind

    @property
    def pocketCards(self):
        return self._pocketCards

    @pocketCards.setter
    def pocketCards(self, cards):
        assert len(cards) == 2
        for card in cards:
            assert card in deck
        self._pocketCards = cards

    @property
    def dealer(self):
        return self._dealer

    @dealer.setter
    def dealer(self, player):
        self._dealer = player

    @property
    def players(self):
        return self._players

    def addPlayer(self, player):
        if player not in self._players:
            self._players.append(player)
        else:
            raise GameError("Player with id {} already listed".format(
                player.playerId))

    def delPlayer(self, player):
        self._players.remove(player)

    def getPlayer(self, id):
        """
        Retrieves a player from the game

        :param id: id of the player
        :return: player
        """
        player = [p for p in self._players if p.playerId == id]
        if len(player) == 1:
            return player[0]
        else:
            raise GameError("Player with id {} not found.".format(id))

    @property
    def gameId(self):
        return self._gameId

    def __eq__(self, other):
        if isinstance(other, Game):
            return self.gameId == other.gameId
        return NotImplemented

    def existRound(self, name):
        """
        Checks if the poker round exists in this game

        :param name: poker round of :obj:`~.Round`
        :return: test if round exists
        """
        position = poker_rounds.index(name)
        if position < len(self._rounds):
            return True
        else:
            return False

    def addRound(self, name, cards=None):
        """
        Adds a poker round to the game

        :param name: poker round of type :obj:`~.Round`
        :param cards: board cards of the round
        """
        position = poker_rounds.index(name)
        if position < len(self._rounds):
            raise GameError("Poker round exists already.")
        elif position == len(self._rounds):
            poker_round = RoundInfo(gameState=name, cards=cards)
            self._rounds.append(poker_round)
        elif position > len(self._rounds):
            raise GameError("Trying to add a poker round at wrong position.")

    @property
    def currRoundInfo(self):
        """
        Current poker round

        :return: poker round
        :rtype: :obj:`~.RoundInfo`
        """
        if self._rounds:
            return self._rounds[-1]
        else:
            raise GameError("No poker round available.")

    @property
    def currRound(self):
        return self.currRoundInfo.gameState

    def existPlayer(self, id):
        """
        Checks if a player exists in the game

        :param id: id of the player
        :return: test if player exists
        """
        try:
            self.getPlayer(id)
        except GameError:
            return False
        return True

    def addAction(self, playerId, kind, money=None):
        """
        Adds an action to the current round of the game

        :param playerId: id of player
        :param kind: type of the action of :obj:`~.Action`
        :param money: stake of the action if available
        """
        if not self.existPlayer(playerId):
            raise GameError("Adding an action of player wiht id {} that "
                            "is not in game.".format(playerId))
        player = self.getPlayer(playerId)
        action = ActionInfo(player=player, kind=kind, money=money)
        self.currRoundInfo.actions.append(action)

    def getActions(self, playerId=None, rounds=None):
        """
        Retrieves actions from the game with optional restrictions on rounds
        and a player.

        :param playerId: id of the player or :obj:`None` for all players
        :param rounds: list of rounds (:obj:`~.Round`) to consider
        :return: list of actions (:obj:`~.Actioninfo`)
        """
        if rounds is not None:
            rounds = [poker_rounds.index(round) for round in rounds]
        else:
            rounds = range(len(self._rounds))
        actions = []
        for poker_round in rounds:
            actions.extend(self._rounds[poker_round].actions)
        if playerId is not None:
            player = self.getPlayer(playerId)
            actions = [action for action in actions if action.player == player]
        return actions

    @property
    def myBet(self):
        if self.currRound == Round.PREFLOP:
            rounds = poker_rounds[:3]
        elif self.currRound == Round.SMALL_BLIND \
                or self.currRound == Round.BIG_BLIND:
            raise GameError("myBet cannot be called while posting blinds.")
        else:
            rounds = [self.currRound]
        myActions = self.getActions(self._myPlayerId, rounds=rounds)
        if myActions:
            return myActions[-1].money
        else:
            return 0

    def startNewHand(self):
        self._rounds = [RoundInfo(gameState=Round.SMALL_BLIND)]
        if self._handNum > 1:  # move dealer button
            dealer_seat = (self.dealer.seat + 1) % len(self.seats)
            self.dealer = [p for p in self.players if p.seat == dealer_seat][0]
        self._handNum += 1
