#!/usr/bin/env python2.7

from config import Config
from irc import IRC
from network import Network

conf = Config()

irc = IRC(conf)
network = Network(conf, irc)

while True:
    data = irc.listen()
    network.dispatch(data)
