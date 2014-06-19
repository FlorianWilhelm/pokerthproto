# -*- coding: utf-8 -*-

from __future__ import print_function, absolute_import, division

from .poker import poker_rounds, Round, Action, deck

__author__ = 'Florian Wilhelm'
__copyright__ = 'Florian Wilhelm'


class ActionInfo(object):
    """
    The action of a player during the poker game.

    :param player: player (:class:`Player`)
    :param kind: type of the action (:class:`Action`)
    :param chips: stake of the action if available
    """

    def __init__(self, player, kind, chips=None):
        self.player = player
        self.kind = kind
        self.chips = chips

    def __eq__(self, other):
        if isinstance(other, ActionInfo):
            return self.__dict__ == other.__dict__
        return NotImplemented


class RoundInfo(object):
    """
    Information about the poker round.

    :param name: name of the poker round (:class:`Round`)
    :param cards: board card of the round as defined in :data:`deck`
    """

    def __init__(self, name, cards=None):
        self._name = name
        self._cards = cards if cards else []
        self._actions = []

    @property
    def actions(self):
        return self._actions

    @property
    def name(self):
        return self._name

    @property
    def cards(self):
        return self._cards

    def __eq__(self, other):
        if isinstance(other, RoundInfo):
            return self.__dict__ == other.__dict__
        return NotImplemented


class GameError(Exception):

    def __unicode__(self):
        return unicode(self.message)

    def __str__(self):
        return unicode(self).encode('utf-8')


class Game(object):
    """
    A poker game holding the information about the actions of the players.
    """
    def __init__(self, gameId):
        self._gameId = gameId
        self._players = []
        self._dealer = None
        self._rounds = []
        self._pocketCards = None
        self._boardCards = []
        self._smallBlind = None
        self._highestSet = 0
        self._minimumRaise = 0
        self._handsPlayed = 0

    @property
    def seats(self):
        seats = sorted([(p.seat, p) for p in self.players])
        return [p for _, p in seats]

    @property
    def handsPlayed(self):
        return self._handsPlayed

    @property
    def minimumRaise(self):
        return self._minimumRaise

    @minimumRaise.setter
    def minimumRaise(self, chips):
        self._minimumRaise = chips

    @property
    def highestSet(self):
        return self._highestSet

    @highestSet.setter
    def highestSet(self, chips):
        self._highestSet = chips

    @property
    def smallBlind(self):
        return self._smallBlind

    @smallBlind.setter
    def smallBlind(self, chips):
        self._smallBlind = chips

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

        :param name: id of the player
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

        :param name: poker round of :class:`Round`
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

        :param name: poker round of type :class:`Round`
        :param cards: board cards of the round
        """
        position = poker_rounds.index(name)
        if position < len(self._rounds):
            raise GameError("Poker round exists already.")
        elif position == len(self._rounds):
            poker_round = RoundInfo(name=name, cards=cards)
            self._rounds.append(poker_round)
            self._highestSet = 0
        elif position > len(self._rounds):
            raise GameError("Trying to add a poker round at wrong position.")

    @property
    def currRound(self):
        """
        Current poker round

        :return: poker round
        :rtype: :class:`Roundinfo`
        """
        if self._rounds:
            return self._rounds[-1]
        else:
            raise GameError("No poker round available.")

    # TODO: Check if this function is still needed
    def isBetPlaced(self):
        """
        Checks if a bet has yet been placed

        :return: test if bet is placed
        :rtype: :obj:`bool`
        """
        round_name = self.currRound.name
        if round_name == Round.SMALL_BLIND or round_name == Round.BIG_BLIND:
            raise GameError("This function should not be called while players "
                            "are posting blinds.")
        if round_name == Round.PREFLOP:
            return True
        for action in self.currRound.actions:
            if action.kind == Action.BET:
                return True
        return False

    # TODO: Check if this function is still needed
    @property
    def currBet(self):
        """
        The current bet if available

        :return: current bet
        """
        round_name = self.currRound.name
        if round_name == Round.SMALL_BLIND or round_name == Round.BIG_BLIND:
            raise GameError("This function should not be called while players "
                            "are posting blinds.")
        curr_bet = 0.
        for action in self.currRound.actions:
            chips = action.chips
            if chips is not None:
                curr_bet = max(curr_bet, chips)
        return curr_bet

    def existPlayer(self, id):
        """
        Checks if a player exists in the game

        :param name: id of the player
        :return: test if player exists
        """
        try:
            self.getPlayer(id)
        except GameError:
            return False
        return True

    def addAction(self, playerId, kind, chips=None):
        """
        Adds an action to the current round of the game

        :param playerId: id of player
        :param kind: type of the action of :class:`Action`
        :param chips: stake of the action if availPlayerIdable
        """
        if not self.existPlayer(playerId):
            raise GameError("Adding an action of player wiht id {} that "
                            "is not in game.".format(playerId))
        player = self.getPlayer(playerId)
        action = ActionInfo(player=player, kind=kind, chips=chips)
        self.currRound.actions.append(action)

    def getActions(self, playerId=None, rounds=None):
        """
        Retrieves actions from the game with optional restrictions on rounds
        and a player.

        :param playerId: id of the player or :obj:`None` for all players
        :param rounds: list of rounds (:class:`Round`) to consider
        :return: found actions :class:`Actioninfo`
        """
        if rounds is not None:
            rounds = [poker_rounds.index(round) for round in rounds]
        else:
            rounds = range(len(self._rounds))
        actions = list()
        for poker_round in rounds:
            actions.extend(self._rounds[poker_round].actions)
        if playerId is not None:
            player = self.getPlayer(playerId)
            actions = [action for action in actions if action.player == player]
        return actions

    def startNewHand(self):
        self._rounds = [RoundInfo(name=Round.SMALL_BLIND)]
        if self._handsPlayed > 0:  # move dealer button
            dealer_seat = (self.dealer.seat + 1) % len(self.seats)
            self.dealer = [p for p in self.players if p.seat == dealer_seat][0]
