============
PokerTHProto
============

.. image:: https://travis-ci.org/FlorianWilhelm/pokerthproto.svg?branch=master
    :target: https://travis-ci.org/FlorianWilhelm/pokerthproto
.. image:: https://coveralls.io/repos/FlorianWilhelm/pokerthproto/badge.png?branch=master
    :target: https://coveralls.io/r/FlorianWilhelm/pokerthproto?branch=master
.. image:: https://requires.io/github/FlorianWilhelm/pokerthproto/requirements.png?branch=master
    :target: https://requires.io/github/FlorianWilhelm/pokerthproto/requirements/?branch=master
    :alt: Requirements Status

The goal of this project is to provide a client interface to a
`PokerTH <http://pokerth.net/>`__ server. This interface could then be used
to write alternative poker clients in Python or even poker bots.

Right now, this project is in a **beta** status, meaning that it is
still incomplete.

Examples
========

PokerTHProto comes with some examples using the `Twisted application framework
<http://twistedmatrix.com/documents/current/core/howto/application.html>`__
which all reside in the ``examples`` folder.

Proxy server
------------

A simple proxy server for PokerTH to inspect the data exchange between client
and server. To use it, run the PokerTH server locally (``pokerth_server``)
and then start the twisted application::

    ./start_proxy.sh

Now run the graphical pokerth client and in *Settings* under the tab
*Internet Game* check *Manual Server Configuration*, choose ``localhost`` as
*Server Address* and ``1234`` as *Server Port* and confirm with *OK*.
Click now *Internet Game* to connect to your local *PokerTH* server and watch
*twisted* logging all messages.

Simple bot
----------

A stupid little poker bot that only checks or calls. With a running PokerTH
server run::

    ./start_client.sh

Then login with the PokerTH GUI and create a game "My Online Game", wait for
the bot to join your game and click ``Start Game``. Don't get too excited if
your are winning ;-)
