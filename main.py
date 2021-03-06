#!/usr/bin/env python3

__title__ = 'pyfoot'
__version__ = '3.0'
__license__ = 'BSD'
__desc__ = (
    'An extensible IRC robot with automatically generated user documentation.')
__url__ = 'https://github.com/colons/pyfoot'

from conf import Config
from irc import IRC
from network import Network
from printer import Printer
from time import sleep
from multiprocessing import Process
import argparse
import signal
import sys
import os


def parse_args():
    """ Set up, and return the results of, the argument parser. """
    parser = argparse.ArgumentParser(
        add_help=False, prog=__title__,
        usage='%(prog)s [options] [logging] network|ALL')

    optional = parser.add_argument_group(title='options')
    log = parser.add_argument_group(title='logging')

    optional.add_argument('-h', '--help', action='help',
                          help='print this help and exit')
    optional.add_argument('-v', '--version', action='version',
                          version='%(prog)s '+__version__,
                          help="show %(prog)s's version and exit")
    optional.add_argument('-c', '--config', dest='config', default=None,
                          help='specify an alternative configuration')
    optional.add_argument('-d', '--daemon', dest='daemonise',
                          action='store_true',
                          help='start %(prog)s in daemon mode')
    optional.add_argument('-p', '--pid', dest='pidfile', metavar='FILE',
                          default=None, help='keep a pid file')

    log.add_argument('-o', '--log', metavar='[FILE]', dest='logfile',
                     default=None, help="log in FILE")
    log.add_argument('-a', '--append', dest='logappend', action='store_true',
                     help="append to FILE when logging")

    parser.add_argument('network',
                        help='an IRC network profile in your configuration')

    return parser.parse_args()


class Robot(Process):
    def __init__(self, network, configfile, logfile, pidfile):
        Process.__init__(self)

        self.network_name = network
        self.configfile_name = configfile
        self.logfile_name = logfile
        self.pidfile_name = pidfile

    def kill_handler(self, signum, frame):
        if signum == signal.SIGINT:
            sig = 'SIGINT'
        elif signum == signal.SIGTERM:
            sig = 'SIGTERM'
        print('\n !! ' + sig + ' caught : warning plugins')

        # Disconnect from the IRC server
        self.network.warn_plugins()
        sleep(2)
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

        self.conf = Config(self.network_name, args.config)
        self.irc = IRC(self.conf)
        self.network = Network(self.conf, self.irc)

        while True:
            data = self.irc.listen()
            self.network.dispatch(data)

    def start_normal(self):
        """ Start pyfoot normally. """
        sys.stderr.write(' -- my process id is ' + str(os.getpid()) + '\n')

        self.start_common()

    def run(self):
        self.start_common()

    def start_threaded(self):
        self.start()

    def start_daemon(self):
        """ Start pyfoot in daemon mode. """
        pid = os.fork()  # First child
        if pid == 0:
            os.setsid()
            pid = os.fork()  # Second child
            if pid != 0:
                sys.stderr.write('now running in the background : '
                                 'my process id is ' + str(pid) + '\n')
                os._exit(0)
        else:
            os._exit(0)

        self.start_common()

if __name__ == '__main__':
    args = parse_args()

    if args.network == 'ALL':
        networks = Config('GLOBAL')['networks']
    else:
        networks = [args.network]

    robots = [Robot(n, args.config, args.logfile, args.pidfile)
              for n in networks]

    if args.daemonise:
        for robot in robots:
            robot.start_daemon()

    elif len(robots) > 1:
        for robot in robots:
            robot.start_threaded()
            print('started %s' % robot)

    else:
        robots[0].start_normal()
