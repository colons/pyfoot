#!/usr/bin/env python2

from network import Network
from conf import NetworkConf
from sys import argv, exit
from os import path

def explain():
    print "Usage: <pyfoot> [[configfile] network]"
    exit(1)

# this whole bit works out what the user specified in arguments
if len(argv) == 3:
    script, configfile, network = argv
elif len(argv) == 2:
    script, network = argv
    configfile = False
elif len(argv) == 1:
    configfile = False
    network = False
else:
    explain()

# this bit tries to fallback to defaults and asks the user for a network if necessary
if not configfile:
    configfile = path.expanduser('~/pyfoot.conf')
    print "No config file specified, using ~/pyfoot.conf"

if not path.exists(configfile):
    print "No config file found, aborting."
    print "An example config file can be found in the root of the source tree."
    explain()

if not network:
    network = raw_input('network: ')

# this bit gets our network's configuration ready
conf = NetworkConf(network, configfile)

# gives the user some comformation
print conf.get('address')

# and goes...
network = Network(conf)
