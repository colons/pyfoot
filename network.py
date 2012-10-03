import message

import sys
import os
import _thread
import re
import plugins

def get_possible_commands(content, commands, plugin_blacklist=[], loose=False):
    """ Return a list of matching command descriptions. """
    possible_commands = []

    for command_dict in [c for c in commands if c['plugin'].name not in plugin_blacklist]:
        args = {}

        if not loose:
            exact_match = command_dict['exact_regex'].match(content)
        else:
            exact_match = False

        if exact_match:
            match = exact_match
        else:
            match = command_dict['fuzzy_regex'].match(content)

        if match:
            if len(match.groups()) > 0:
                i = 1
                for arg in command_dict['arglist']:
                    args[arg] = match.group(i)
                    i += 1

            command_dict['args'] = args

            if exact_match:
                return [command_dict]
            else:
                possible_commands.append(command_dict)

    return possible_commands


def command_to_regex_and_arglist(command, loose=False):
    """ Take a command and return an exact and fuzzy regex and a list of arguments. ignore_variables if you're help.py, and we'll omit the exact regex. """
    fuzzy_regex = ''

    if not loose:
        exact_regex = ''

    arglist = []

    if loose:
        first_word = True

    for word in command.split(' '):
        if loose and not first_word:
            fuzzy_regex += '(?:\s*$|'

        if loose:
            first_word = False

        arg = re.match('<(\S+)>$', word)

        if arg:
            if re.match('<<(\S+)>>$', word):
                arglist.append(arg.group(1)[1:-1])
                if loose:
                    fuzzy_regex += '(.*)\s*'
                else:
                    fuzzy_regex += '(.+)\s+'
                    exact_regex += '(.+)\s+'
            else:
                arglist.append(arg.group(1))
                if loose:
                    fuzzy_regex += '(\S*)\s*'
                else:
                    fuzzy_regex += '(\S+)\s+'
                    exact_regex += '(\S+)\s+'
        else:
            if not loose:
                exact_regex += word

            try:
                fuzzy_regex += word[0]
            except IndexError:
                # this is an attempt to register <comchar> as a command
                pass

            for letter in word[1:]:
                fuzzy_regex += '(?:\\b|[%s]' % letter
            for letter in word[1:]:
                fuzzy_regex += ')'

            if loose:
                fuzzy_regex += '\s*'
            else:
                fuzzy_regex += '\s+'
                exact_regex += '\s+'

    # strip final whitespace requirements; they're only necessary between words
    fuzzy_regex = fuzzy_regex[:-3]

    if loose:
        for word in command.split(' ')[1:]:
            fuzzy_regex += ')'
    else:
        exact_regex = exact_regex[:-3]


    if not loose:
        fuzzy_regex += '$'
        exact_regex += '$'

    compiled_fuzzy_regex = re.compile(fuzzy_regex)

    if not loose:
        compiled_exact_regex = re.compile(exact_regex)
        return compiled_exact_regex, compiled_fuzzy_regex, arglist
    else:
        return compiled_fuzzy_regex, arglist




class Network(object):
    def __init__(self, conf, irc):
        self.initial = True
        self.conf = conf
        self.irc = irc
        self.plugins = []
        self.all_commands = []
        self.all_regexes = []

        plugins.__path__.insert(0, '%s/plugins' % conf.conf['content_dir'])

        for plugin_name in conf.conf['plugins']:
            __import__('plugins.'+plugin_name)
            plugin = sys.modules['plugins.%s' % plugin_name]

            try:
                plugin.defaults
            except AttributeError:
                pass
            else:
                for key in plugin.defaults:
                    if key not in conf.conf:
                        conf.conf[key] = plugin.defaults[key]

            setattr(plugin.Plugin, 'name', plugin_name)
            plugin_instance = plugin.Plugin(self.irc, conf)

            self.plugins.append(plugin_instance)

            for command, function in self.plugins[-1].commands:
                exact_regex, fuzzy_regex, arglist = command_to_regex_and_arglist(command)
                self.all_commands.append({
                    'command': command,
                    'exact_regex': exact_regex,
                    'fuzzy_regex': fuzzy_regex,
                    'arglist': arglist,
                    'function': function,
                    'plugin': plugin_instance
                    })

            for regex, function in plugin_instance.regexes:
                self.all_regexes.append((re.compile(regex), function, plugin_instance))

        for plugin in self.plugins:
            plugin.network = self

            try:
                plugin.prefork()
            except AttributeError:
                pass

            plugin.setDaemon(True)
            plugin.start()





    def delegate(self, the_message):
        nick_blacklist = [n.lower() for n in self.conf.conf['nick_blacklist']]

        try:
            plugin_blacklist = [m.lower() for m in self.conf.conf['plugin_blacklist'][the_message.source.lower()]]
        except KeyError:
            plugin_blacklist = []

        if the_message.content.startswith(self.conf.conf['comchar']):
            commands = get_possible_commands(the_message.content[len(self.conf.conf['comchar']):].rstrip(), self.all_commands, plugin_blacklist=plugin_blacklist)
            ambiguity = len(commands)

            if ambiguity == 1:
                command_dict = commands[0]
                command_dict['args']['_command'] = command_dict['command']
                command_dict['plugin'].queue.put((command_dict['function'], the_message, command_dict['args']))

            elif ambiguity > 1:
                self.irc.privmsg(the_message.source, '\x02ambiguous command\x02\x03# |\x03 %s' % ' \x03#:\x03 '.join(
                    [self.conf.conf['comchar']+c['command'].replace('>>', '>').replace('<<', '<') for c in commands]))

        for regex, function, plugin in self.all_regexes:
            match = regex.match(the_message.content)

            if match:
                if plugin.name.lower() not in plugin_blacklist and the_message.nick.lower() not in self.conf.conf['nick_blacklist']:
                    plugin.queue.put((function, the_message, match))


    def dispatch(self, data):
        """ Deals with messages and sends plugins the information they need. """
        if data == None:
            print(' :: no data')
            return None

        if data == b'':
            print(' :: empty response, assuming disconnection\a') # alert
            sys.exit()


        for line in [line for line in data.split(b'\r\n') if len(line) > 0]:
            line_raw = line
            try:
                line = line.decode(self.irc.charset)
            except UnicodeDecodeError:
                print("\n !! Some characters could not be reproduced in the below input using 'charset': '%s'" % self.irc.charset)
                if len(line) == 512:
                    print(' !! The input length was at maximum; the message may have been truncated.')
                line = line.decode(self.irc.charset, 'ignore')

            #print('    %s' % repr(line_raw))
            print('    %s' % line)

            if line.startswith('PING :'):
                self.irc.pong(line)
                continue

            the_message = message.Message(line, line_raw)

            if the_message.type == '353':
                # this is a channel names list
                pass

            if the_message.type == '324':
                # this is a list of channel modes
                splitline = line.split(' ')
                name = splitline[3]
                modelist = splitline[4]
                try:
                    self.irc.channels[name]['modes'] = modelist
                except KeyError:
                    self.irc.channels[name] = {}
                    self.irc.channels[name]['modes'] = modelist

            elif the_message.type == 'JOIN':
                if line.startswith(':%s!%s@' % (self.conf.conf['nick'], self.conf.conf['username'])):
                    self.irc.own_hostname = line.split(' ')[0][1:]
                    print(' -- we are %s' % self.irc.own_hostname)
                if self.initial:
                    self.initial = False


            elif the_message.type == 'INVITE':
                channel = the_message.content
                print(' -- we were invited to %s by %s' % (channel, the_message.nick))
                self.irc.join(channel)

            elif the_message.type == 'KICK':
                channel = the_message.source
                print(' -- we were kicked from %s by %s' % (channel, the_message.nick))
                self.irc.part(channel, kick=True)

            elif the_message.type == 'NOTICE':
                pass

            elif the_message.type == 'NICK':
                pass

            elif the_message.type == 'MODE' and self.initial == True:
                for channel in self.conf.conf['network_channels']:
                    self.irc.join(channel)

            elif the_message.type == 'MODE':
                self.irc.getmode(line.split(' ')[2])

            elif the_message.type == 'PRIVMSG':
                self.delegate(the_message)
