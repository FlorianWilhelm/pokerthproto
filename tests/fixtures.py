# -*- coding: utf-8 -*-

from __future__ import print_function, absolute_import, division

import os
import tempfile
from subprocess import check_call
from shutil import rmtree

import pytest

from pokerthproto.pokerth_pb2 import PokerTHMessage

__author__ = 'Florian Wilhelm'
__copyright__ = 'Florian Wilhelm'


@pytest.fixture
def initMsgData():
    return b'\x00\x00\x00\x1c\x08\x02\x1a\x18\n\x04\x08\x05\x10\x01' \
        '\x10\x00(\x022\x0cHuman Player'


@pytest.fixture
def initMsg():
    msg = PokerTHMessage()
    msg.ParseFromString(initMsgData()[4:])
    return msg


@pytest.yield_fixture()
def tmpdir():
    old_path = os.getcwd()
    newpath = tempfile.mkdtemp()
    os.chdir(newpath)
    yield
    os.chdir(old_path)
    rmtree(newpath)


@pytest.yield_fixture()
def pokerth_server():
    with tempfile.NamedTemporaryFile(dir='./') as fh:
        check_call('pokerth_server -p {}'.format(fh.name), shell=True)
        yield
        check_call('kill {}'.format(fh.read()), shell=True)
