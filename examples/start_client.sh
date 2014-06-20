#!/bin/bash

PIDFILE=`pwd`/pokerth_server.pid

pokerth_server -p $PIDFILE

twistd -y pokerth_client.tac -n --pidfile=pokerth_client.pid

kill `cat $PIDFILE`
rm $PIDFILE
