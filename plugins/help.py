import re

from bottle import template
from markdown import markdown

from plugin import Plugin
from network import command_to_regex_and_arglist, get_possible_commands


def genderise(line, conf):
    for pnoun_type in conf['pnoun_neutral']:
        match_pnoun = conf['pnoun_neutral'][pnoun_type]
        repl_pnoun = conf['pnoun'][pnoun_type]

        pn_regex = r'(?i)\b(%s)\b' % match_pnoun

        for match in re.findall(pn_regex, line):
            if match[0].isupper():
                repl = repl_pnoun.capitalize()
            else:
                repl = repl_pnoun.lower()

            line = re.sub(pn_regex, repl, line, count=1)

    return line


class Plugin(Plugin):
    def register_commands(self):
        self.commands = [
            ('help', self.all_help),
            ('help <<subject>>', self.specific_help),
        ]

    def register_urls(self):
        self.urls = []

        if self.conf.alias == 'GLOBAL':
            self.urls.append(('/help/', self.help_page))
        else:
            self.urls.append(('/help/%s/' % self.conf.alias, self.help_page))

    def postfork(self):
        # we can't build our command regexes until we fork;
        # self.network.all_commands will not exist when prepare() is called
        self.argless_commands = []

        for orig_dict in self.network.all_commands:
            command_dict = orig_dict.copy()
            command_dict['fuzzy_regex'], command_dict['arglist'] = \
                command_to_regex_and_arglist(command_dict['command'],
                                             loose=True)

            self.argless_commands.append(command_dict)

    def list_commands(self, message, args):
        """
        Lists every documented command.
        """

        commands = [self.conf['comchar']+c['command']
                    for c in self.network.all_commands
                    if c['function'].__doc__]
        self.irc.privmsg(message.source, ' \x03#:\x03 '.join(commands),
                         crop=False)

    def specific_help(self, message, args):
        """
        Get help for a particular command.

        $<comchar>he <comchar>h

        >\x02hhg\x02\x03# |\x03 <comchar>hhg &lt;character&gt;\x03# :\x03
        <comchar>hhg\x03# |\x03 http://woof.bldm.us/help/<network>/#hhg

        >\x02help\x02\x03# |\x03 <comchar>help\x03# :\x03
        <comchar>help &lt;subject&gt;\x03# |\x03
        http://woof.bldm.us/help/<network>/#help
        """

        if args['subject'].startswith(self.conf['comchar']):
            command = args['subject'][len(self.conf['comchar']):]
        else:
            command = args['subject']

        possibilities = get_possible_commands(command,
                                              self.argless_commands,
                                              loose=True)

        plugins = {}
        for possibility in possibilities:
            plugin = possibility['plugin']
            if plugin.name not in plugins:
                plugins[plugin.name] = []

            command = possibility['command'].replace(
                '>>', '>').replace('<<', '<')

            plugins[plugin.name].append(
                '%s%s' % (self.conf['comchar'], command))

        outlist = []

        for plugin in plugins:
            commands = '\x03# :\x03 '.join(plugins[plugin])
            outlist.append('\x02%s\x02\x03# |\x03 %s\x03# |\x03 %s/help/%s/#%s'
                           % (plugin, commands, self.conf['web_url'],
                              self.conf.alias, plugin))

        for out in outlist:
            self.irc.privmsg(message.source, out)

        if len(outlist) == 0:
            self.irc.privmsg(
                message.source, '\x02%s\x02\x03# |\x03 no such command\x03# '
                '|\x03 see %s/help/%s/' % (args['subject'],
                                           self.conf['web_url'],
                                           self.conf.alias))

    def all_help(self, message, args):
        """
        Returns links to this page and to pyfoot's [source
        code](https://github.com/colons/pyfoot/) and [issue
        tracker](https://github.com/colons/pyfoot/issues/new)

        $<comchar>help

        >\x02features\x02\x03# :\x03 http://woof.bldm.us/help/<network>/\x03# |
        \x03\x02 code\x02\x03# :\x03 https://github.com/colons/pyfoot\x03#
        |\x03\x02 bug?\x02\x03# :\x03
        https://github.com/colons/pyfoot/issues/new
        """

        self.irc.privmsg(
            message.source, '\x02features\x02\x03# :\x03 %s/help/%s/\x03# '
            '|\x03\x02 code\x02\x03# :\x03 https://github.com/colons/pyfoot'
            '\x03# |\x03\x02 bug?\x02\x03# :\x03 https://github.com/colons/'
            'pyfoot/issues/new' % (self.conf['web_url'], self.conf.alias))

    def help_page(self):
        behaviour = markdown(genderise(
            'On startup, %s will join all the channels xyr configuration '
            'suggests xe should. Channels joined and left while running do not'
            ' change this.\n\n'
            'While running, xe will join any channel xe receives an [invitatio'
            'n](http://www.irchelp.org/irchelp/rfc/chapter4.html#c4_2_7) to. '
            'Xe will, under no circumstances, automatically rejoin a channel '
            'when kicked. If you want xem back, re-invite xem.'
            % self.conf['nick'], self.conf))

        return template('docs', plugins=self.bottle.networks[self.conf.alias],
                        conf=self.conf, per_network=True, behaviour=behaviour)
