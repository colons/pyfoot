import socket
import ssl
import sys
import re


class IRC(object):
    """ An IRC connection """
    def __init__(self, conf):
        """ Connects to a network """
        self.channels = {}
        self.own_hostname = False

        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect(
                (conf.get('network_address'), conf.get('network_port'))
                )

        if ssl:
            self.socket = ssl.wrap_socket(self.socket)

        self.socket.send('NICK %s\r\n' % conf.get('nick'))
        self.socket.send('USER %s %s %s %s\r\n' % (
                conf.get('username'),
                conf.get('hostname'),
                conf.get('servername'),
                conf.get('realname')
                )
            )

        if conf.conf['network_nickserv_pass']:
            self.privmsg('NickServ', 'identify %s' % conf.get('network_nickserv_pass'))

        self.quit_message = conf.get('quit_message')


    def pong(self, data):
        """ Maybe falling into parser ground a little, we develop and send a ping response """
        self.socket.send('PONG %s\r\n' % data.split()[1])


    def who(self, user):
        self.socket.send('WHO %s' % user)


    def join(self, channel):
        """ Joins a channel. """
        self.socket.send('JOIN %s\r\n' % channel)
        self.getmode(channel)


    def part(self, channel, reason=''):
        self.socket.send('PART %s %s\r\n' % (channel, reason))

        if channel in self.channels:
            del self.channels[channel]


    def getmode(self, name):
        self.socket.send('MODE %s\r\n' % name)


    def who(self, host):
        self.socket.send('WHO %s\r\n' % host)


    def act(self, target, message, pretty=False, crop=True):
        self.ctcp(target, 'ACTION', message, notice=False, crop=crop)


    def send(self, message):
        print ' >> %s' % message
        self.socket.send(message.encode('utf-8')) if isinstance(message, unicode) else self.socket.send(message)


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

        out = '%s %s :\x01%s\x01\r\n' % (message_type, target, s)
        self.send(out)


    def privmsg(self, target, message, pretty=False, crop=True):
        """ Sends a channel or user a message. If the message exceeds the 512 character limit, it gets cropped. """
        if pretty:
            message = self.beautify(message)

        try:
            if 'c' in self.channels[target]['modes']:
                message = self.strip_formatting(message)
        except KeyError:
            pass

        message = self.crop(message, 'PRIVMSG', target)

        out = 'PRIVMSG %s :%s\r\n' % (target, message)
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
        self.data = self.socket.recv(4096)

        if self.data.find(' '):
            return self.data


    def quit(self, reason=None):
        reason = reason or self.quit_message
        out = 'QUIT :%s\r\n' % reason
        print ''
        self.send(out)
        sys.exit()
