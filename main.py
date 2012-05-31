#!/usr/bin/env python3.2

__title__ = 'pyfoot'
__version__ = '3.0'
__license__ = 'WTFPL'
__desc__ = 'An extensible IRC robot with automatically generated user documentation.'
__url__ = 'https://github.com/colons/pyfoot'

from conf import Config
from irc import IRC
from network import Network
from printer import Printer
import argparse
import signal
import sys
import os

def parse_args():
    """ Set up, and return the results of, the argument parser. """
    parser = argparse.ArgumentParser(add_help=False, prog=__title__, usage='%(prog)s [options] [logging] network')
    required = parser.add_argument_group(title='required')
    optional = parser.add_argument_group(title='options')
    log = parser.add_argument_group(title='logging')

    required.add_argument('network', help='an IRC network profile in your configuration')

    optional.add_argument('-h', '--help', action='help', help='print this help and exit')
    optional.add_argument('-v', '--version', action='version', version='%(prog)s '+__version__, help="show %(prog)s's version and exit")
    optional.add_argument('-c', '--config', dest='config', default=None, help='specify an alternative configuration')
    optional.add_argument('-d', '--daemon', dest='daemonise', action='store_true', help='start %(prog)s in daemon mode')
    optional.add_argument('-p', '--pid', dest='pidfile', metavar='FILE', default=None, help='keep a pid file')

    log.add_argument('-o', '--log', metavar='[FILE]', dest='logfile', default=None, help="log in FILE")
    log.add_argument('-a', '--append', dest='logappend', action='store_true', help="append to FILE when logging")
    return parser.parse_args()

class Robot(object):
    def __init__(self, network, configfile, logfile, pidfile):
        self.network_name = network
        self.configfile_name = configfile
        self.logfile_name = logfile
        self.pidfile_name = pidfile

    def kill_handler(self, signum, frame):
        if signum == signal.SIGINT:
            sig = 'SIGINT'
        elif signum == signal.SIGTERM:
            sig = 'SIGTERM'
        print('\n !! ' + sig + ' caught : shutting down')

        # Disconnect from the IRC server
        self.irc.quit()

        # Delete the pid file and close the log file for a clean exit
        if args.pidfile:
            os.remove(args.pidfile)
        if args.logfile:
            print(' @@ end of log\n')
        sys.exit()

    def start_common(self):
        """ Things that both daemonised and normal startup will do """
        if self.logfile_name:
            print(' @@ start of log')
            
        if self.pidfile_name:
            pidfile = open(args.pidfile, 'wt', encoding='us-ascii')
            pidfile.write(str(os.getpid()))
            pidfile.close()

        sys.stdout = Printer(args.logfile, args.logappend, args.daemonise)

        signal.signal(signal.SIGTERM, self.kill_handler)
        signal.signal(signal.SIGINT, self.kill_handler)

        self.conf = Config(args.network, args.config)
        self.irc = IRC(self.conf)
        self.network = Network(self.conf, self.irc)

        # main event loop
        while True:
            data = self.irc.listen()
            self.network.dispatch(data)

    def start_normal(self):
        """ Start pyfoot normally. """
        sys.stderr.write(' -- my process id is ' + str(os.getpid()) + '\n')
        self.start_common()

    # Derived from http://code.activestate.com/recipes/278731-creating-a-daemon-the-python-way/
    def start_daemon(self):
        """ Start pyfoot in daemon mode. """
        pid = os.fork()  # First child
        if pid == 0:
            os.setsid()
            pid = os.fork()  # Second child
            if pid != 0:
                sys.stderr.write('now running in the background : my process id is ' + str(pid) + '\n')
                os._exit(0)
        else:
            os._exit(0)

        self.start_common()

if __name__ == '__main__':
    # Parse the command line arguments
    # A --help/-h or --version/-v will end the program here
    args = parse_args()

    pyfoot = Robot(args.network, args.config, args.logfile, args.pidfile)

    if args.daemonise == True:
        pyfoot.start_daemon()
    else:
        pyfoot.start_normal()
