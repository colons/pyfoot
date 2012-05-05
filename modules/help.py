import module

class Module(module.Module):
    def register_commands(self):
        self.commands = [
                ('help', self.all_help),
                ('help <module>', self.targetted_help),
                ]

    def targetted_help(self, message, args):
        if args['module'] in self.conf.get('modules'):
            self.irc.send(message.source, '\x02%s\x02 | http://woof.bldm.us/help/%s#%s' % (args['module'], self.conf.alias, args['module']), pretty=True)
        else:
            self.irc.send(message.source, '\x02%s\x02 | no such module' % args['module'], pretty=True)

    def all_help(self, message, args):
        """ Returns links to this page and to pyfoot's <a href="https://bitbucket.org/colons/pyfoot/">source code</a> and <a href="https://bitbucket.org/colons/pyfoot/issues/new">issue tracker</a>.
        $<comchar>help
        >\x02features\x02\x034 :\x03 http://woof.bldm.us/help/<network>\x034 |\x03\x02 code\x02\x034 :\x03 https://bitbucket.org/colons/pyfoot\x034 |\x03\x02 bug?\x02\x034 :\x03 https://bitbucket.org/colons/pyfoot/issues/new
        """
        self.irc.send(message.source, '\x02features\x02\x034 :\x03 http://woof.bldm.us/help/%s/\x034 |\x03\x02 code\x02\x034 :\x03 https://bitbucket.org/colons/pyfoot\x034 |\x03\x02 bug?\x02\x034 :\x03 https://bitbucket.org/colons/pyfoot/issues/new' % self.conf.alias)
