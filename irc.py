import socket
import ssl
from django.utils.encoding import smart_str
import sys
import re

def split_len(seq, length):
    """ Splits messages into manageable chunks """
    """ Thanks to http://code.activestate.com/recipes/496784-split-string-into-n-size-pieces/ """
    return [seq[i:i+length] for i in range(0, len(seq), length)]


class IRC(object):
    """ Our IRC abstraction layer - this object represents the actual connection """
    def __init__(self, address, port, nick, username, hostname, servername, realname, ssl_enabled=False):
        """ Connects to a network """
        raw_irc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        raw_irc.connect((address, int(port)))

        if ssl_enabled:
            self.irc = ssl.wrap_socket(raw_irc)
        else:
            self.irc = raw_irc

        self.irc.send('NICK %s\r\n' % nick)
        self.irc.send('USER %s %s %s %s\r\n' % (username, hostname, servername, realname))
        self.channels = {}

    def pong(self, data):
        """ Maybe falling into parser ground a little, we develop and send a ping response """
        self.irc.send('PONG %s\r\n' % data.split()[1])
    
    def whois(self, user):
        """ Performs a WHOIS operation and returns the response. INCOMPLETE. """
        self.irc.send('WHOIS %s' % user)
        self.listen

    def is_registered(self, user):
        """ Determines if a user is registered. INCOMPLETE. """
        self.whois(user)

    def join(self, channel):
        """ Joins a channel. If already joined, requests channel modes. """
        try:
            self.channels[channel]
        except KeyError:
            # we are not in this channel
            print ' :: Joining %s' % channel
            self.irc.send('JOIN %s\r\n' % channel)

        self.irc.send('MODE %s\r\n' % channel)

    def send(self, channel, message, pretty=False, crop=False):
        """ Sends a channel (or user) a message. If the message exceeds 420 characters, it gets split up. """
        message_list = split_len(message, 420)
        
        if crop and len(message_list) > 1:
            message_list = [message_list[0]]
            message_list[0] = message_list[0][:-3].rstrip()+'...'

        for part in message_list:
            if pretty:
                part = self.beautify(part)

            try:
                if 'c' in self.channels[channel]:
                    part = self.strip_formatting(part)
            except KeyError:
                pass

            out = 'PRIVMSG %s :%s\r\n' % (channel, smart_str(part))
            print ' >>', out,
            self.irc.send(out)

    def beautify(self, message):
        message = message.replace(' :: ', '\x034 ::\x03 ')
        message = message.replace(' : ', '\x034 :\x03 ')
        message = message.replace(' | ', '\x034 |\x03 ')
        message = message.replace(' @ ', '\x034 @\x03 ')
        return message

    def strip_formatting(self, part):

        # colours first
        odd = True
        while re.search('\x03', part):
            if odd:
                part = re.sub('\x03\d?\d?', '', part, count=1)
            else:
                part = re.sub('\x03', '', part, count=1)

            odd = not odd
        
        part = re.sub('\x01', '', part)
        part = re.sub('\x02', '', part)
        part = re.sub('\x0F', '', part)
        part = re.sub('\x16', '', part)

        return part
        
    def listen(self):
        """ Listens for incoming stuffs and returns them """
        self.data = self.irc.recv(4096)
        
        if self.data.find(' '):
            return self.data

    def close(self):
        self.irc.close
        sys.exit()
