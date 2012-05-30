#!/usr/bin/env python3.2

__title__ = 'pyfoot'
__version__ = '3.3'
__license__ = 'WTFPL'
__desc__ = 'An extensible IRC robot with automatically generated user documentation.'
__url__ = 'https://github.com/colons/pyfoot'

from conf import Config
from irc import IRC
from network import Network
import argparse
import signal

def parse_args():
    """ Set up, and return the results of, the argument parser. """
    parser = argparse.ArgumentParser(description=__desc__, add_help=False, prog=__title__)
    required = parser.add_argument_group(title='Required')
    optional = parser.add_argument_group(title='Optional')

    required.add_argument('network', help='an IRC network profile in your configuration')
    optional.add_argument('--help', '-h', action='help', help='print this help and exit')
    optional.add_argument('--version', '-v', action='version', version='%(prog)s '+__version__, help="show %(prog)s's version and exit")
    optional.add_argument('--config', '-c', dest='config', default=None, help='specify an alternative configuration')
    optional.add_argument('--daemon', '-d', dest='start', action='store_const', const=start_daemon, default=start_normal, help='start %(prog)s in daemon mode')
    return parser.parse_args()

# Thank you http://code.activestate.com/recipes/278731-creating-a-daemon-the-python-way/
def start_daemon():
    """ Start pyfoot in daemon mode. """
    import os

    # Constants
    if (hasattr(os, 'devnull')):
        REDIRECT_TO  = os.devnull
    else:
        REDIRECT_TO = '/dev/null'
    MAXFD = 1024

    pid = os.fork()  # First child
    if pid == 0:
        os.setsid()
        pid = os.fork()  # Second child
        if pid != 0:
            print('now running in the background : my process id is ' + str(pid))
            os._exit(0)
    else:
        os._exit(0)

    # Check maximum file descriptor or set to default
    import resource
    maxfd = resource.getrlimit(resource.RLIMIT_NOFILE)[1]
    if (maxfd == resource.RLIM_INFINITY):
        maxfd = MAXFD

    # Iterate through and close all file descriptors.
    for fd in range(0, maxfd):
        try:
            os.close(fd)
        except OSError: # ERROR, fd wasn't open to begin with (ignored)
            pass

    # This call to open is guaranteed to return the lowest file descriptor,
    # which will be 0 (stdin), since it was closed above.
    os.open(REDIRECT_TO, os.O_RDWR)  # standard input (0)

    # Duplicate standard input to standard output and standard error.
    os.dup2(0, 1)  # standard output (1)
    os.dup2(0, 2)  # standard error (2)

    start_normal(False)

def start_normal(nodaemon=True):
    """ Start pyfoot. """
    if nodaemon:
        from os import getpid
        print(' -- my process id is ' + str(getpid()))

    conf = Config(args.network, args.config)
    irc = IRC(conf)
    network = Network(conf, irc)

    def kill_handler(signum, frame):
        if signum == signal.SIGINT:
            sig = 'SIGINT'
        elif signum == signal.SIGTERM:
            sig = 'SIGTERM'
        print('\n !! ' + sig + ' caught : shutting down')
        irc.quit()

    signal.signal(signal.SIGTERM, kill_handler)
    signal.signal(signal.SIGINT, kill_handler)

    while True:
        data = irc.listen()
        network.dispatch(data)

if __name__ == '__main__':
    args = parse_args()
    args.start()
