# -*- coding: utf-8 -*-

from __future__ import print_function, absolute_import, division

from pokerthproto import poker
from pokerthproto import game
from pokerthproto import player

import pytest

__author__ = 'Florian Wilhelm'
__copyright__ = 'Florian Wilhelm'


def test_ActionInfo():
    p1 = player.Player(1)
    action1 = game.ActionInfo(p1, poker.Action.ALLIN)
    action2 = game.ActionInfo(p1, poker.Action.ALLIN)
    assert action1 == action2
    assert action1.__eq__(object) == NotImplemented
    print(action1)


def test_rounds():
    pgame = game.Game(1, 1)
    with pytest.raises(game.GameError):
        pgame.currRoundInfo()
    pgame.addRound(poker.Round.SMALL_BLIND)
    assert pgame.currRoundInfo.name == 'SMALL_BLIND'
    assert len(pgame.currRoundInfo.cards) == 0
    with pytest.raises(game.GameError):
        pgame.addRound(poker.Round.SMALL_BLIND)
    assert pgame.existRound(poker.Round.SMALL_BLIND)
    assert not pgame.existRound(poker.Round.RIVER)
    assert pgame.currRound == poker.Round.SMALL_BLIND
    with pytest.raises(game.GameError):
        pgame.addRound(poker.Round.FLOP)
    other_round = game.RoundInfo(poker.Round.SMALL_BLIND)
    assert pgame.currRoundInfo == other_round
    assert other_round.__eq__(object) == NotImplemented
    print(pgame.currRoundInfo)


def test_players():
    pgame = game.Game(1, 1)
    player1 = player.Player(1)
    pgame.addPlayer(player1)
    assert pgame.existPlayer(1)
    assert not pgame.existPlayer(2)
    assert len(pgame.players) == 1
    other_player1 = pgame.getPlayer(1)
    assert player1 == other_player1
    pgame.delPlayer(player1)
    assert len(pgame.players) == 0


def test_actions():
    pgame = game.Game(1, 1)
    player1 = player.Player(1)
    pgame.addPlayer(player1)
    player2 = player.Player(2)
    pgame.addPlayer(player2)
    pgame.addRound(poker.Round.SMALL_BLIND)
    pgame.addRound(poker.Round.BIG_BLIND)
    pgame.addRound(poker.Round.PREFLOP)
    pgame.addAction(1, poker.Action.BET, 1.0)
    with pytest.raises(game.GameError):
        pgame.addAction(42, poker.Action.BET)
    actions = pgame.getActions(1)
    assert len(actions) == 1
    assert actions[0].kind == poker.Action.BET
    pgame.addAction(1, poker.Action.RAISE, 2.0)
    actions = pgame.getActions(1)
    assert len(actions) == 2
    assert actions[1].kind == poker.Action.RAISE
    pgame.addRound(poker.Round.FLOP)
    pgame.addAction(2, poker.Action.BET, 1.0)
    pgame.addAction(1, poker.Action.FOLD)
    actions = pgame.getActions(1)
    assert len(actions) == 3
    assert actions[2].kind == poker.Action.FOLD
    actions = pgame.getActions(1, rounds=[poker.Round.FLOP])
    assert len(actions) == 1
    assert actions[0].kind == poker.Action.FOLD
    actions = pgame.getActions()
    assert len(actions) == 4
    actions = pgame.getActions(rounds=[poker.Round.FLOP])
    assert len(actions) == 2


def test_GameError():
    err = game.GameError("message")
    print(err)


def test_Game():
    pgame = game.Game(1, 1)
    assert pgame == game.Game(1, 1)
    assert pgame.__eq__(object) == NotImplemented
    player1 = player.Player(1)
    player1.seat = 1
    pgame.addPlayer(player1)
    player2 = player.Player(2)
    player2.seat = 2
    pgame.addPlayer(player2)
    with pytest.raises(game.GameError):
        pgame.addPlayer(player2)
    assert pgame.seats == [player1, player2]
    assert pgame.handNum == 1
    pgame.minimumRaise = 10
    assert pgame.minimumRaise == 10
    pgame.highestSet = 100
    assert pgame.highestSet == 100
    pgame.smallBlind = 5
    assert pgame.smallBlind == 5
    assert pgame.bigBlind == 10
    pgame.pocketCards = ['2h', 'Tc']
    assert pgame.pocketCards == ['2h', 'Tc']
    pgame.dealer = player1
    assert pgame.dealer == player1
    pgame.addRound(poker.Round.SMALL_BLIND)
    assert pgame.existRound(poker.Round.SMALL_BLIND)
    assert not pgame.existRound(poker.Round.BIG_BLIND)
    assert pgame.currRoundInfo.name == "SMALL_BLIND"


def test_myBet():
    pgame = game.Game(1, 1)
    player1 = player.Player(1)
    pgame.addPlayer(player1)
    pgame.addRound(poker.Round.SMALL_BLIND)
    pgame.addAction(1, poker.Action.NONE, 10)
    pgame.addRound(poker.Round.BIG_BLIND)
    pgame.addAction(1, poker.Action.NONE, 20)
    with pytest.raises(game.GameError):
        pgame.myBet()
    pgame.addRound(poker.Round.PREFLOP)
    assert pgame.myBet == 20
    pgame.addAction(1, poker.Action.RAISE, 30)
    assert pgame.myBet == 30
    pgame.addRound(1, poker.Round.FLOP)
    assert pgame.myBet == 0


def test_startNewHand():
    pgame = game.Game(1, 1)
    player1 = player.Player(1)
    player1.seat = 0
    pgame.addPlayer(player1)
    player2 = player.Player(2)
    player2.seat = 1
    pgame.addPlayer(player2)
    pgame.dealer = player1
    pgame.startNewHand()
    pgame.currRound == poker.Round.SMALL_BLIND
    assert pgame.dealer == player1
    assert pgame.handNum == 2
    pgame.startNewHand()
    assert pgame.dealer == player2
