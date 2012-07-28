from auth import Authenticator
import plugin

defaults = {
        'admin_salt_length': 32,
        'admin_key_length': 32,
        'admin_key_iters': 10000,
        'admin_key_hash': 'sha256',

        'admin_admins': {
            },
        }

class Plugin(plugin.Plugin):
    def prepare(self):
        self.authenticated_hosts = {}

        self.auth = Authenticator(
                self.conf.conf['admin_key_length'],
                self.conf.conf['admin_salt_length'],
                self.conf.conf['admin_key_iters'],
                self.conf.conf['admin_key_hash']
                )

    def register_commands(self):
        self.commands = [
                ('auth <pass>', self.authenticate),
                ('mkpasswd <pass>', self.make_passkey),
                ('sit', self.sit),
                ('say <target> <<message>>', self.say),
                ('act <target> <<message>>', self.act),
                ('ctcp <target> <ctcp> <<content>>', self.ctcp),
                ('ctcp <target> <ctcp>', self.solo_ctcp),
                ('join <channel>', self.join),
                ('part <channel> <<reason>>', self.part_with_reason),
                ('part <channel>', self.part),
                ]

    def authenticate(self, message, args):
        """ Authenticate with <pyfoot>. """
        try:
            pword_conf = self.conf.conf['admin_admins'][message.nick]
        except KeyError:
            self.irc.act(message.source, 'growls')
            return

        pword_msg = b' '.join(message.content_raw.split(b' ')[1:])
        print('\a !! auth attempt by ' + message.nick)

        if self.auth.check_passkey(pword_conf, pword_msg) == True:
            self.authenticated_hosts[message.host] = message.nick
            self.irc.privmsg(message.source, 'woof')
        else:
            self.irc.act(message.source, 'growls')

    def make_passkey(self, message, args):
        """ Make a passkey for use with <pyfoot>. """
        pword_msg = b' '.join(message.content_raw.split(b' ')[1:])
        new_passkey = self.auth.make_passkey(pword_msg)
        self.irc.privmsg(message.source, new_passkey)

    def can_trust(self, message):
        if message.host in self.authenticated_hosts and self.authenticated_hosts[message.host] == message.nick:
            return True
        else:
            self.irc.act(message.source, 'growls')
            return False

    def act(self, message, args):
        """ Make <pyfoot> do something. """
        if self.can_trust(message):
            self.irc.act(args['target'], args['message'])

    def say(self, message, args):
        """ Make <pyfoot> say something. """
        if self.can_trust(message):
            self.irc.privmsg(args['target'], args['message'])

    def ctcp(self, message, args):
        """ Send a CTCP message. Content optional. """
        if self.can_trust(message):
            self.irc.ctcp(args['target'], args['ctcp'], args['content'])

    def solo_ctcp(self, message, args):
        if self.can_trust(message):
            self.irc.ctcp(args['target'], args['ctcp'])

    def join(self, message, args):
        """ Make <pyfoot> join a channel. """
        if self.can_trust(message):
            self.irc.join(args['channel'])
            self.irc.privmsg(message.source, 'joined ' + args['channel'])

    def part_with_reason(self, message, args):
        """ Make <pyfoot> leave a channel. Reason optional. """
        if self.can_trust(message):
            self.irc.part(args['channel'], args['reason'])
            self.irc.privmsg(message.source, 'left ' + args['channel'])

    def part(self, message, args):
        if self.can_trust(message):
            self.irc.part(args['channel'])
            self.irc.privmsg(message.source, 'left ' + args['channel'])

    def sit(self, message, args):
        """ Test authentication state. """
        if self.can_trust(message):
            self.irc.act(message.source, 'sits')
