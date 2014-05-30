============
PokerTHProto
============

The goal of this project is to provide an client interface to a
`PokerTH <http://pokerth.net/>`__ server. This interface could then be used
to write alternative poker clients in Python or even poker bots.

Right now, this project is in a **pre-alpha** status, meaning that it is
rather incomplete and does not yet fulfill its purpose. The only functionality
that works right now is to provide an simple proxy in order to inspect the
messages between an PokerTH client and server.

Usage
=====

Start the Pokerth server locally::

    pokerth_server

and then start the twisted application in the ``examples`` folder::

    twisted -y pokerth_proxy.tac -n

Now start the graphical pokerth client and in *Settings* under the tab
*Internet Game* check *Manual Server Configuration*, choose ``localhost`` as
*Server Address* and ``1234`` as *Server Port* and confirm with *OK*.
Click now *Internet Game* to connect to your local *PokerTH* server and watch
twisted logging all messages.
