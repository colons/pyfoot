#!/usr/bin/env python3.2

__title__ = 'pyfoot'
__version__ = '3.0'
__license__ = 'WTFPL'
__desc__ = 'An extensible IRC robot with automatically generated user documentation.'
__url__ = 'https://github.com/colons/pyfoot'

from conf import Config
from irc import IRC
from network import Network
import argparse

def parse_args():
    parser = argparse.ArgumentParser(description=__desc__, add_help=False, prog=__title__)
    required = parser.add_argument_group(title='Required')
    optional = parser.add_argument_group(title='Optional')

    optional.add_argument('--help', '-h', action='help', help='print this help and exit')
    optional.add_argument('--version', '-v', action='version', version='%(prog)s '+__version__, help="show %(prog)s's version and exit")
    optional.add_argument('--config', '-c', dest='config', default=None, help='specify an alternative configuration')
    required.add_argument('network', help='an IRC network profile in your configuration')
    return parser.parse_args()

args = parse_args()
conf = Config(args.network, args.config)

irc = IRC(conf)
network = Network(conf, irc)

while True:
    try:
        data = irc.listen()
        network.dispatch(data)
    except KeyboardInterrupt:
        irc.quit()
