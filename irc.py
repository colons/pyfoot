import socket
import ssl
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
        self.initial = True # this gets set to false once all channels have been joined

        self.channels = {}
        self.people = {}

        raw_irc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        raw_irc.connect((address, int(port)))

        if ssl_enabled:
            self.irc = ssl.wrap_socket(raw_irc)
        else:
            self.irc = raw_irc

        self.irc.send('NICK %s\r\n' % nick)
        self.irc.send('USER %s %s %s %s\r\n' % (username, hostname, servername, realname))
        

    def pong(self, data):
        """ Maybe falling into parser ground a little, we develop and send a ping response """
        self.irc.send('PONG %s\r\n' % data.split()[1])

    
    def who(self, user):
        self.irc.send('WHO %s' % user)
        self.listen


    def join(self, channel):
        """ Joins a channel. If already joined, requests channel modes. """
        try:
            self.channels[channel]
        except KeyError:
            # we are not in this channel
            print ' :: Joining %s' % channel
            self.irc.send('JOIN %s\r\n' % channel)
            self.getmode(channel)


    def getmode(self, name):
        self.irc.send('MODE %s\r\n' % name)

    
    def who(self, host):
        self.irc.send('WHO %s\r\n' % host)

    
    def act(self, target, message, pretty=False, crop=False):
        self.ctcp(target, 'ACTION', message, notice=False)


    def ctcp(self, target, ctcp, message=None, notice=False):
        """ Issue a CTCP """
        if message:
            s = ctcp+' '+message
        else:
            s = ctcp

        if notice:
            message_type = 'NOTICE'
        else:
            message_type = 'PRIVMSG'

        out = '%s %s :\x01%s\x01\r\n' % (message_type, target, s)
        self.irc.send(out)

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
                if 'c' in self.channels[channel]['modes']:
                    part = strip_formatting(part)
            except KeyError:
                pass

            part = part.encode('utf-8') if type(part) is unicode else part
            out = 'PRIVMSG %s :%s\r\n' % (channel, part)
            print ' >>', out,
            self.irc.send(out)


    def beautify(self, message):
        message = message.replace(' :: ', '\x034 ::\x03 ')
        message = message.replace(' : ', '\x034 :\x03 ')
        message = message.replace(' | ', '\x034 |\x03 ')
        message = message.replace(' @ ', '\x034 @\x03 ')
        return message


        
    def listen(self):
        """ Listens for incoming stuffs and returns them """
        self.data = self.irc.recv(4096)
        
        if self.data.find(' '):
            return self.data


    def close(self, reason):
        print 'irc.close(\'%s\') invoked, shutting down' % reason
        self.irc.send('QUIT :%s\r\n' % reason)
