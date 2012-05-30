import socket
import ssl
from sys import exit
import re


class IRC(object):
    """ An IRC connection """
    def __init__(self, conf):
        """ Connects to a network """
        self.channels = {}
        self.own_hostname = False

        self.conf = conf
        self.charset = conf.conf['charset']

        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect(
                (conf.conf['network_address'], conf.conf['network_port'])
                )

        if ssl:
            self.socket = ssl.wrap_socket(self.socket)

        # The socket object is basically a wrapper for the OS's socket implementation.
        # As such, it has no knowledge of character sets, thus every call to socket.send()
        # must send a bytes object rather than a string, hence the encode() calls.

        self.socket.send(('NICK %s\r\n' % conf.conf['nick']).encode(self.charset))
        self.socket.send(('USER %s %s %s %s\r\n' % (
                conf.conf['username'],
                conf.conf['hostname'],
                conf.conf['servername'],
                conf.conf['realname']
                )).encode(self.charset)
            )

        try:
            # The more secure and direct way to identify. Not sure how to handle it if the server
            # doesn't recognise the NICKSERV command, but that's what the issue tracker is for.
            self.send(('NICKSERV identify %s' % conf.conf['network_nickserv_pass']))
            #self.privmsg('NickServ', 'identify %s' % conf.conf['network_nickserv_pass'])
        except KeyError:
            pass

        self.quit_message = conf.conf['quit_message']


    def pong(self, data):
        """ Maybe falling into parser ground a little, we develop and send a ping response """
        self.socket.send(('PONG %s\r\n' % data.split()[1]).encode(self.charset))


    def who(self, user):
        self.socket.send(('WHO %s' % user).encode(self.charset))


    def join(self, channel):
        """ Joins a channel. """
        out = 'JOIN %s' % channel
        self.send(out)
        self.getmode(channel)


    def part(self, channel, reason='', kick=False):
        if not kick:
            self.send(('PART %s %s' % (channel, reason)).encode(self.charset))

        if channel in self.channels:
            del self.channels[channel]


    def getmode(self, name):
        self.socket.send(('MODE %s\r\n' % name).encode(self.charset))


    def who(self, host):
        self.socket.send('WHO %s\r\n' % host)


    def act(self, target, message, pretty=False, crop=True):
        self.ctcp(target, 'ACTION', message, notice=False, crop=crop)

    def send(self, message):
            print(' >> %s' % message)
            message += '\r\n'
            try:
                self.socket.send(message.encode(self.charset))
            except UnicodeEncodeError:
                print("\n !! Some characters could not be reproduced in the proceding output using 'charset': " + self.charset)
                self.socket.send(message.encode(self.charset, 'ignore'))


    def ctcp(self, target, ctcp, message=None, notice=False, crop=True):
        """ Issue a CTCP message """
        if notice:
            message_type = 'NOTICE'
        else:
            message_type = 'PRIVMSG'

        if message:
            message = self.crop(message, message_type+ctcp+'\x01 \x01', target)
            s = ctcp+' '+message
        else:
            s = ctcp

        out = '%s %s :\x01%s\x01' % (message_type, target, s)
        self.send(out)


    def privmsg(self, target, message, pretty=False, crop=True):
        """ Sends a channel or user a message. If the message exceeds the 512 character limit, it gets cropped. """
        if pretty:
            message = self.beautify(message)

        message = self.add_missing_colours(message)

        try:
            if 'c' in self.channels[target]['modes']:
                message = self.strip_formatting(message)
        except KeyError:
            pass

        message = self.crop(message, 'PRIVMSG', target)

        out = 'PRIVMSG %s :%s' % (target, message)
        self.send(out)


    def crop(self, message, command, target):
        """ Crops a message based on how long the command will be on the client side --- IRC can not exceed 512 characters, we must account for this.
        message is the type of message you're sending. It's only used for length, so feel free to include \\x01\\x01 in CTCP messages, etc. """
        cruft = len(':%s %s %s :' % (self.own_hostname, command, target))
        excess = (len(message) - (512 - cruft))

        if excess > 0:
            message = message[:-(excess+5)].rstrip()+'...'

        return message

    def beautify(self, message):
        message = message.replace(' : ', ' \x03#:\x03 ')
        message = message.replace(' | ', ' \x03#|\x03 ')
        return message

    def add_missing_colours(self, message):
        assem = ''
        split = message.split('\x03')
        assem = split[0]

        if len(split)>0:
            for part in split[1:]:
                assem += '\x03'
                if part.startswith('#'):
                    assem += str(self.conf.conf['pigment'])
                    assem += part[1:]
                else:
                    assem += part

        return assem

    def strip_formatting(self, part):
        part = re.sub('\x03\d?\d?((?=[^,])|,\d?\d?)', '', part)
        part = re.sub('[\x01\x02\x0F\x16]', '', part)
        #part = re.sub('\x01', '', part)
        #part = re.sub('\x02', '', part)
        #part = re.sub('\x0F', '', part)
        #part = re.sub('\x16', '', part)

        return part


    def listen(self):
        """ Listens for incoming stuffs and returns them """
        self.data = self.socket.recv(4096)

        if self.data.find(b' '):
            return self.data


    def quit(self, reason=None):
        reason = reason or self.quit_message
        out = 'QUIT :%s' % reason
        self.send(out)
        print()
        exit()
