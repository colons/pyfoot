import module

class Module(module.Module):
    def register_commands(self):
        self.regexes = [
                ('\x01VERSION\x01', self.ctcp),
                ]

    def ctcp(self, message, args):
        """ Get version information. """
        self.irc.ctcp(message.source, 'VERSION', 'pyfoot; see %s' % self.conf.get('web_url'), notice=True)
