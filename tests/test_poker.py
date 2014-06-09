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


def test_round_actions():
    gameInfo = poker.GameInfo()
    game = poker.Game(1, pokerth_pb2.netGameCreated, gameInfo, False, 1)
    with pytest.raises(poker.GameStateError):
        game.currRound()
    game.addRound(poker.Round.SMALL_BLIND)
    assert game.existRound(poker.Round.SMALL_BLIND)
    assert not game.existRound(poker.Round.RIVER)
    assert game.currRound.name == poker.Round.SMALL_BLIND
    with pytest.raises(poker.GameStateError):
        game.addRound(poker.Round.FLOP)

