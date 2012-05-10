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

        for orig_dict in self.network.all_commands:
            command_dict = orig_dict.copy()
            command_dict['fuzzy_regex'], command_dict['arglist'] = command_to_regex_and_arglist(command_dict['command'], loose=True)

            self.argless_commands.append(command_dict)

    def specific_help(self, message, args):
        """ Get help for a particular command.
        $<comchar>he <comchar>h
        >\x02hhg\x02\x03# |\x03 <comchar>hhg &lt;character&gt;\x03# :\x03 <comchar>hhg\x03# |\x03 http://woof.bldm.us/help/<network>/#hhg
        >\x02help\x02\x03# |\x03 <comchar>help\x03# :\x03 <comchar>help &lt;subject&gt;\x03# |\x03 http://woof.bldm.us/help/<network>/#help"""

        if args['subject'].startswith(self.conf.get('comchar')):
            command = args['subject'][len(self.conf.get('comchar')):]
        else:
            command = args['subject']

        possibilities = get_possible_commands(command, self.argless_commands)
        
        modules = {}
        for possibility in possibilities:
            module = possibility['module']
            if module.name not in modules:
                modules[module.name] = []

            command = possibility['command'].replace('>>', '>').replace('<<', '<')

            modules[module.name].append('%s%s' % (self.conf.get('comchar'), command))

        outlist = []

        for module in modules:
            commands = '\x03# :\x03 '.join(modules[module])
            outlist.append('\x02%s\x02\x03# |\x03 %s\x03# |\x03 %shelp/%s/#%s' % (module, commands, self.conf.get('web_url'), self.conf.alias, module))
        
        for out in outlist:
            self.irc.privmsg(message.source, out)

        if len(outlist) == 0:
            self.irc.privmsg(message.source, '\x02%s\x02\x03# |\x03 no such command\x03# |\x03 see http://woof.bldm.us/help/%s/' % (args['subject'], self.conf.alias))


    def all_help(self, message, args):
        """ Returns links to this page and to pyfoot's <a href="https://github.com/colons/pyfoot/">source code</a> and <a href="https://github.com/colons/pyfoot/issues/new">issue tracker</a>.
        $<comchar>help
        >\x02features\x02\x03# :\x03 http://woof.bldm.us/help/<network>/\x03# |\x03\x02 code\x02\x03# :\x03 https://github.com/colons/pyfoot\x03# |\x03\x02 bug?\x02\x03# :\x03 https://github.com/colons/pyfoot/issues/new
        """
        self.irc.privmsg(message.source, '\x02features\x02\x03# :\x03 http://woof.bldm.us/help/%s/\x03# |\x03\x02 code\x02\x03# :\x03 https://github.com/colons/pyfoot\x03# |\x03\x02 bug?\x02\x03# :\x03 https://github.com/colons/pyfoot/issues/new' % self.conf.alias)
