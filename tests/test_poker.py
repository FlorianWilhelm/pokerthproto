# -*- coding: utf-8 -*-

from __future__ import print_function, absolute_import, division

from pokerthproto import poker

__author__ = 'Florian Wilhelm'
__copyright__ = 'Florian Wilhelm'


def test_cardToInt_and_intToCard():
    results = {'2d': 0,
               'Ad': 12,
               '2h': 13,
               'Ah': 25,
               '2s': 26,
               'As': 38,
               '2c': 39,
               'Ac': 51}
    for c, i in results.items():
        assert poker.cardToInt(c) == i
        assert poker.intToCard(i) == c
    for card in poker.deck:
        assert card == poker.intToCard(poker.cardToInt(card))
