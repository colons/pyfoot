#!/usr/bin/env python2.7

from conf import Config
from irc import IRC
from network import Network
from sys import argv

conf = Config(argv[-1])

irc = IRC(conf)
network = Network(conf, irc)

while True:
    data = irc.listen()
    network.dispatch(data)
