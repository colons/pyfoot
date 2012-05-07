import module
import sha

class Module(module.Module):
    def prepare(self):
        self.authenticated_hosts = {}
        self.sha = sha.new(self.conf.get('admin_salt'))

    def register_commands(self):
        self.commands = [
                ('auth <pass>', self.authenticate),
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
        sha = self.sha.copy()
        sha.update(args['pass'])
        
        print '\a !! auth attempt' % sha.hexdigest()
        if sha.hexdigest() == self.conf.get('admin_admins')[message.nick]:
            self.authenticated_hosts[message.host] = message.nick

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
            self.irc.send(args['target'], args['message'])

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
    
    def part_with_reason(self, message, args):
        """ Make <pyfoot> leave a channel. Reason optional. """
        if self.can_trust(message):
            self.irc.part(args['channel'], args['reason'])

    def part(self, message, args):
        if self.can_trust(message):
            self.irc.part(args['channel'])

    def sit(self, message, args):
        """ Test authentication state. """
        if self.can_trust(message):
            self.irc.act(message.source, 'sits')
