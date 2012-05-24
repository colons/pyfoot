#!/usr/bin/env python2.7

from conf import Config
from irc import IRC
from network import Network
from sys import argv, exit

def usage():
    print "main.py network [config]"

if len(argv) == 2:
    conf = Config(argv[1])
elif len(argv) == 3:
    conf = Config(argv[1], argv[2])
else:
    usage()
    exit()

irc = IRC(conf)
network = Network(conf, irc)

while True:
    try:
        data = irc.listen()
        network.dispatch(data)
    except KeyboardInterrupt:
        irc.quit()
