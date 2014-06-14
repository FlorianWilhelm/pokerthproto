# -*- coding: utf-8 -*-

from __future__ import print_function, absolute_import, division

from . import pokerth_pb2

__author__ = 'Florian Wilhelm'
__copyright__ = 'Florian Wilhelm'


# suits of poker cards (diamonds, hearts, spades, clubs)
suits = ['d', 'h', 's', 'c']
# ranks of poker cards (Ace, Jack, Queens, King, Ten, ...)
ranks = ['2', '3', '4', '5', '6', '7', '8', '9', 'T', 'J', 'Q', 'K', 'A']
# deck of poker cards
deck = [r + s for r in ranks for s in suits]


class Action(object):
    """
    Enum of possible player actions in poker
    """
    NONE = pokerth_pb2.netActionNone
    FOLD = pokerth_pb2.netActionFold
    CHECK = pokerth_pb2.netActionCheck
    CALL = pokerth_pb2.netActionCall
    BET = pokerth_pb2.netActionBet
    RAISE = pokerth_pb2.netActionRaise
    ALLIN = pokerth_pb2.netActionAllIn


class Round(object):
    """
    Enum of poker rounds where posting blinds is considered a round too
    """
    SMALL_BLIND = pokerth_pb2.netStatePreflopSmallBlind
    BIG_BLIND = pokerth_pb2.netStatePreflopBigBlind
    PREFLOP = pokerth_pb2.netStatePreflop
    FLOP = pokerth_pb2.netStateFlop
    TURN = pokerth_pb2.netStateTurn
    RIVER = pokerth_pb2.netStateRiver


poker_rounds = [Round.SMALL_BLIND, Round.BIG_BLIND, Round.PREFLOP, Round.FLOP,
                Round.TURN, Round.RIVER]


def cardToInt(card):
    assert len(card) == 2
    return 13*suits.index(card[1]) + ranks.index(card[0])


def intToCard(i):
    assert 0 <= i <= 51
    return ranks[i % 13] + suits[i // 13]
