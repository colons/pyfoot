from module import Module
from network import command_to_regex_and_arglist, get_possible_commands

class Module(Module):
    def register_commands(self):
        self.commands = [
                ('help', self.all_help),
                ('help <<subject>>', self.specific_help),
                ]

    def prefork(self):
        # we can't build our command regexes until we fork;
        # self.network.all_commands will not exist when prepare() is called
        self.argless_commands = []

        for command, regex, arglist, function, module in self.network.all_commands:
            argless_regex, arglist = command_to_regex_and_arglist(command, ignore_variables=True)
            self.argless_commands.append((command, argless_regex, arglist, function, module))

    def specific_help(self, message, args):
        """ Get help for a module or command. Commands can be shortened beyond ambiguity.
        $<comchar>help help
        >\x02help\x02\x034 |\x03 http://woof.bldm.us/help/<network>/#help
        $<comchar>he <comchar>h
        >\x02hhg\x02\x034 |\x03 <comchar>hhg &lt;character&gt;\x034 :\x03 <comchar>hhg\x034 |\x03 http://woof.bldm.us/help/<network>/#hhg
        >\x02help\x02\x034 |\x03 <comchar>help\x034 :\x03 <comchar>help &lt;subject&gt;\x034 |\x03 http://woof.bldm.us/help/<network>/#help"""

        if args['subject'].startswith(self.conf.get('comchar')):
            command = args['subject'][len(self.conf.get('comchar')):]
            possibilities = get_possible_commands(command, self.argless_commands)
            
            modules = {}
            for command, module, function, arglist in possibilities:
                if module.name not in modules:
                    modules[module.name] = []

                command = command.replace('>>', '>').replace('<<', '<')

                modules[module.name].append('%s%s' % (self.conf.get('comchar'), command))

            outlist = []

            for module in modules:
                commands = '\x034 :\x03 '.join(modules[module])
                outlist.append('\x02%s\x02\x034 |\x03 %s\x034 |\x03 %shelp/%s/#%s' % (module, commands, self.conf.get('web_url'), self.conf.alias, module))
            
            for out in outlist:
                self.irc.send(message.source, out)

            if len(outlist) == 0:
                self.irc.send(message.source, '\x02%s\x02\x034 |\x03 no such command\x034 |\x03 see http://woof.bldm.us/help/%s/' % (args['subject'], self.conf.alias))

        elif args['subject'] in self.conf.get('modules'):
            self.irc.send(message.source, '\x02%s\x02 | http://woof.bldm.us/help/%s/#%s' % (args['subject'], self.conf.alias, args['subject']), pretty=True)

        else:
            self.irc.send(message.source, '\x02%s\x02 | no such module\x034 |\x03 see http://woof.bldm.us/help/%s/' % (args['subject'], self.conf.alias), pretty=True)

    def all_help(self, message, args):
        """ Returns links to this page and to pyfoot's <a href="https://bitbucket.org/colons/pyfoot/">source code</a> and <a href="https://bitbucket.org/colons/pyfoot/issues/new">issue tracker</a>.
        $<comchar>help
        >\x02features\x02\x034 :\x03 http://woof.bldm.us/help/<network>/\x034 |\x03\x02 code\x02\x034 :\x03 https://bitbucket.org/colons/pyfoot\x034 |\x03\x02 bug?\x02\x034 :\x03 https://bitbucket.org/colons/pyfoot/issues/new
        """
        self.irc.send(message.source, '\x02features\x02\x034 :\x03 http://woof.bldm.us/help/%s/\x034 |\x03\x02 code\x02\x034 :\x03 https://bitbucket.org/colons/pyfoot\x034 |\x03\x02 bug?\x02\x034 :\x03 https://bitbucket.org/colons/pyfoot/issues/new' % self.conf.alias)
