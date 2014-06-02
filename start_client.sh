#!/bin/bash

PIDFILE=`pwd`/pokerth_server.pid

pokerth_server -p $PIDFILE

twistd -y examples/pokerth_client.tac -n

kill `cat $PIDFILE`
rm $PIDFILE
