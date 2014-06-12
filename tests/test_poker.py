# -*- coding: utf-8 -*-

from __future__ import print_function, absolute_import, division

import pytest

from pokerthproto import poker
from pokerthproto import pokerth_pb2

__author__ = 'Florian Wilhelm'
__copyright__ = 'Florian Wilhelm'


def test_cardToInt_and_intToCard():
    results = {'2d': 0, 'Ad': 12, '2h': 13, 'Ah': 25, '2s': 26, 'As': 38,
               '2c': 39, 'Ac': 51}
    for c, i in results.items():
        assert poker.cardToInt(c) == i
        assert poker.intToCard(i) == c
    for card in poker.deck:
        assert card == poker.intToCard(poker.cardToInt(card))


def test_rounds():
    gameInfo = poker.GameInfo()
    game = poker.Game(1, pokerth_pb2.netGameCreated, gameInfo, False, 1)
    with pytest.raises(poker.GameStateError):
        game.currRound()
    game.addRound(poker.Round.SMALL_BLIND)
    with pytest.raises(poker.GameStateError):
        game.addRound(poker.Round.SMALL_BLIND)
    assert game.existRound(poker.Round.SMALL_BLIND)
    assert not game.existRound(poker.Round.RIVER)
    assert game.currRound.name == poker.Round.SMALL_BLIND
    with pytest.raises(poker.GameStateError):
        game.addRound(poker.Round.FLOP)


def test_isBetPlaced():
    gameInfo = poker.GameInfo()
    game = poker.Game(1, pokerth_pb2.netGameCreated, gameInfo, False, 1)
    game.addRound(poker.Round.SMALL_BLIND)
    with pytest.raises(poker.GameStateError):
        game.isBetPlaced()
    game.addRound(poker.Round.BIG_BLIND)
    with pytest.raises(poker.GameStateError):
        game.isBetPlaced()
    game.addRound(poker.Round.PREFLOP)
    assert game.isBetPlaced()
    game.addRound(poker.Round.FLOP)
    assert not game.isBetPlaced()
    player = poker.Player(1)
    game.addPlayer(player)
    game.addAction(1, poker.Action.BET, 2.5)
    assert game.isBetPlaced()


def test_currBet():
    gameInfo = poker.GameInfo()
    game = poker.Game(1, pokerth_pb2.netGameCreated, gameInfo, False, 1)
    game.addRound(poker.Round.SMALL_BLIND)
    with pytest.raises(poker.GameStateError):
        game.currBet
    player = poker.Player(1)
    game.addPlayer(player)
    game.addRound(poker.Round.BIG_BLIND)
    with pytest.raises(poker.GameStateError):
        game.currBet
    game.addRound(poker.Round.PREFLOP)
    game.addAction(1, poker.Action.BET, 1.0)
    assert game.currBet == 1.0


def test_existPlayer():
    gameInfo = poker.GameInfo()
    game = poker.Game(1, pokerth_pb2.netGameCreated, gameInfo, False, 1)
    player = poker.Player(1)
    game.addPlayer(player)
    assert game.existPlayer(1)
    assert not game.existPlayer(2)


def test_actions():
    gameInfo = poker.GameInfo()
    game = poker.Game(1, pokerth_pb2.netGameCreated, gameInfo, False, 1)
    player = poker.Player(1)
    game.addPlayer(player)
    player = poker.Player(2)
    game.addPlayer(player)
    game.addRound(poker.Round.SMALL_BLIND)
    game.addRound(poker.Round.BIG_BLIND)
    game.addRound(poker.Round.PREFLOP)
    game.addAction(1, poker.Action.BET, 1.0)
    actions = game.getActions(1)
    assert len(actions) == 1
    assert actions[0].kind == poker.Action.BET
    game.addAction(1, poker.Action.RAISE, 2.0)
    actions = game.getActions(1)
    assert len(actions) == 2
    assert actions[1].kind == poker.Action.RAISE
    game.addRound(poker.Round.FLOP)
    game.addAction(2, poker.Action.BET, 1.0)
    game.addAction(1, poker.Action.FOLD)
    actions = game.getActions(1)
    assert len(actions) == 3
    assert actions[2].kind == poker.Action.FOLD
    actions = game.getActions(1, rounds=[poker.Round.FLOP])
    assert len(actions) == 1
    assert actions[0].kind == poker.Action.FOLD
    actions = game.getActions()
    assert len(actions) == 4
    actions = game.getActions(rounds=[poker.Round.FLOP])
    assert len(actions) == 2
