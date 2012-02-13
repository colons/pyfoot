import socket
from django.utils.encoding import smart_str

def split_len(seq, length):
    """ Splits messages into manageable chunks """
    """ Thanks to http://code.activestate.com/recipes/496784-split-string-into-n-size-pieces/ """
    return [seq[i:i+length] for i in range(0, len(seq), length)]


class IRC(object):
    """ Our IRC abstraction layer - this object represents the actual connection """
    def __init__(self, address, port, nick, username, hostname, servername, realname):
        """ Connects to a network """
        self.irc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.irc.connect((address, int(port)))
        self.irc.send('NICK %s\r\n' % nick)
        self.irc.send('USER %s %s %s %s\r\n' % (username, hostname, servername, realname))

    def pong(self, data):
        """ Maybe falling into parser ground a little, we develop and send a ping response """
        self.irc.send('PONG %s\r\n' % data.split()[1])

    def join(self, channel):
        """ Joins a channel """
        self.irc.send('JOIN %s\r\n' % channel)

    def send(self, channel, message):
        """ Sends a channel (or user) a message. If the message exceeds 420 characters, it gets split up. """
        message_list = split_len(message, 420)
        for part in message_list:
            out = 'PRIVMSG %s :%s\r\n' % (channel, smart_str(part))
            print ' >>', out,
            self.irc.send(out)
        
    def listen(self):
        """ Listens for incoming stuffs and returns them """
        self.data = self.irc.recv(4096)
        
        if self.data.find(' '):
            return self.data

