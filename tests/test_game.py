# -*- coding: utf-8 -*-

from __future__ import print_function, absolute_import, division

from pokerthproto import poker
from pokerthproto import game
from pokerthproto import player

import pytest

__author__ = 'Florian Wilhelm'
__copyright__ = 'Florian Wilhelm'


def test_rounds():
    pgame = game.Game(1)
    with pytest.raises(game.GameError):
        pgame.currRound()
    pgame.addRound(game.Round.SMALL_BLIND)
    with pytest.raises(game.GameError):
        pgame.addRound(poker.Round.SMALL_BLIND)
    assert pgame.existRound(poker.Round.SMALL_BLIND)
    assert not pgame.existRound(poker.Round.RIVER)
    assert pgame.currRound.name == poker.Round.SMALL_BLIND
    with pytest.raises(game.GameError):
        pgame.addRound(poker.Round.FLOP)


def test_isBetPlaced():
    pgame = game.Game(1)
    pgame.addRound(poker.Round.SMALL_BLIND)
    with pytest.raises(game.GameError):
        pgame.isBetPlaced()
    pgame.addRound(poker.Round.BIG_BLIND)
    with pytest.raises(game.GameError):
        pgame.isBetPlaced()
    pgame.addRound(poker.Round.PREFLOP)
    assert pgame.isBetPlaced()
    pgame.addRound(poker.Round.FLOP)
    assert not pgame.isBetPlaced()
    player1 = player.Player(1)
    pgame.addPlayer(player1)
    pgame.addAction(1, poker.Action.BET, 2.5)
    assert pgame.isBetPlaced()


def test_currBet():
    pgame = game.Game(1)
    pgame.addRound(poker.Round.SMALL_BLIND)
    with pytest.raises(game.GameError):
        pgame.currBet
    player1 = player.Player(1)
    pgame.addPlayer(player1)
    pgame.addRound(poker.Round.BIG_BLIND)
    with pytest.raises(game.GameError):
        pgame.currBet
    pgame.addRound(poker.Round.PREFLOP)
    pgame.addAction(1, poker.Action.BET, 1.0)
    assert pgame.currBet == 1.0


def test_players():
    pgame = game.Game(1)
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
    pgame = game.Game(1)
    player1 = player.Player(1)
    pgame.addPlayer(player1)
    player2 = player.Player(2)
    pgame.addPlayer(player2)
    pgame.addRound(poker.Round.SMALL_BLIND)
    pgame.addRound(poker.Round.BIG_BLIND)
    pgame.addRound(poker.Round.PREFLOP)
    pgame.addAction(1, poker.Action.BET, 1.0)
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
