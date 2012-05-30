import sys
import os

# Derived from http://stackoverflow.com/a/616672
# and http://code.activestate.com/recipes/278731-creating-a-daemon-the-python-way/
class Printer(object):
    """ Custom printer class
    Allows for logging of all print() statements as well as redirecting console output to /dev/null (daemon mode)
    """
    def __init__(self, logfile=None, append=True, silent=False):
        if silent:
            import resource
            MAXFD = 1024
            maxfd = resource.getrlimit(resource.RLIMIT_NOFILE)[1]
            if (maxfd == resource.RLIM_INFINITY):
                maxfd = MAXFD

            # Iterate through and close all file descriptors.
            for fd in range(0, maxfd):
                try:
                    os.close(fd)
                except OSError: # fd wasn't open to begin with (ignored)
                    pass

            # This call to open is guaranteed to return the lowest file descriptor,
            # which will be 0 (stdin), since it was closed above.
            self.terminal = os.open(os.devnull, os.O_RDWR)  # standard input (0)
            os.dup2(0, 1)  # standard output (1)
            os.dup2(0, 2)  # standard output (2)

        self.terminal = sys.stdout

        if logfile:
            # append's default is True to avoid accidental overwrites,
            # but client code really should regulate this on its own.
            if append:
                self.logfile = open(logfile, 'at', encoding='utf-8')
                self.logfile.write('\n')
            else:
                self.logfile = open(logfile, 'wt', encoding='utf-8')
        else:
            self.logfile = None


    def write(self, message):
        self.terminal.write(message)
        if self.logfile:
            self.logfile.write(message)

    def flush(self):
        self.terminal.flush()
        if self.logfile:
            self.logfile.flush()
