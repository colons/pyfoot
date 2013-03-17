import socket
import ssl
import re


class IRC(object):
    """ An IRC connection """
    def __init__(self, conf):
        """ Connects to a network """
        self.channels = {}
        self.own_hostname = False

        self.conf = conf
        self.charset = conf['charset']

        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect(
            (conf['network_address'], conf['network_port'])
        )

        if ssl:
            self.socket = ssl.wrap_socket(self.socket)

        self.socket.send(('NICK %s\r\n' % conf['nick']).encode(self.charset))
        self.socket.send(('USER %s %s %s %s\r\n' % (
            conf['username'],
            conf['hostname'],
            conf['servername'],
            conf['realname']
        )).encode(self.charset)
        )

        try:
            self.send(('NICKSERV identify %s' % conf['network_nickserv_pass']))
        except KeyError:
            pass

        self.quit_message = conf['quit_message']

    def pong(self, data):
        """ Send a ping response """
        self.socket.send(('PONG %s\r\n'
                          % data.split()[1]).encode(self.charset))

    def join(self, channel):
        """ Joins a channel. """
        out = 'JOIN %s' % channel
        self.send(out)
        self.getmode(channel)

    def part(self, channel, reason='', kick=False):
        if not kick:
            self.send('PART %s %s' % (channel, reason))

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
                print("\n !! Some characters could not be reproduced in the "
                      "proceding output using 'charset': " + self.charset)
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
        """
        Send a channel or user a message. If the message exceeds the 512
        character limit (and crop is True), truncate it.
        """

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
        """
        Crop a message based on how long the command will be on the client side
        -- IRC can not exceed 512 characters, we must account for this.

        message is the type of message you're sending. It's only used for
        length, so feel free to include \\x01\\x01 in CTCP messages, etc.
        """

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

        if len(split) > 0:
            for part in split[1:]:
                assem += '\x03'
                if part.startswith('#'):
                    assem += str(self.conf['pigment'])
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
