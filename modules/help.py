import module

class Module(module.Module):
    def register_commands(self):
        self.commands = [
                ('help', self.send_help),
                ]

    def send_help(self, message, args):
        """ Returns links to this page and to pyfoot's <a href="https://bitbucket.org/colons/pyfoot/">source code</a> and <a href="https://bitbucket.org/colons/pyfoot/issues/new">issue tracker</a>.
        $<comchar>help
        >\x02features\x02\x034 :\x03 http://woof.bldm.us/help/<network>\x034 |\x03\x02 code\x02\x034 :\x03 https://bitbucket.org/colons/pyfoot\x034 |\x03\x02 bug?\x02\x034 :\x03 https://bitbucket.org/colons/pyfoot/issues/new
        """
        self.irc.send(message.source, '\x02features\x02\x034 :\x03 http://woof.bldm.us/help/%s/\x034 |\x03\x02 code\x02\x034 :\x03 https://bitbucket.org/colons/pyfoot\x034 |\x03\x02 bug?\x02\x034 :\x03 https://bitbucket.org/colons/pyfoot/issues/new' % self.conf.alias)
