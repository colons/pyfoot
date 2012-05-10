import message

import sys
import os
import thread
import re
import modules

def get_possible_commands(content, commands, module_blacklist=[]):
    """ Return a list of matching command descriptions. """
    possible_commands = []

    for command_dict in [c for c in commands if c['module'].name not in module_blacklist]:
        args = {}
        
        exact_match = command_dict['exact_regex'].match(content)
        
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
                print ' -- exact match!'
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

            fuzzy_regex += word[0]

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
        self.irc = irc
        self.modules = []
        self.all_commands = []
        self.all_regexes = []

        modules.__path__.insert(0, '%s/modules' % conf.get('content_dir'))

        for modulename in conf.get('modules'):
            __import__('modules.'+modulename)
            module = sys.modules['modules.'+modulename]
            setattr(module.Module, 'name', modulename)
            self.modules.append(module.Module(self.irc, conf))

            for command, function in self.modules[-1].commands:
                exact_regex, fuzzy_regex, arglist = command_to_regex_and_arglist(command)
                self.all_commands.append({
                    'command': command, 
                    'exact_regex': exact_regex,
                    'fuzzy_regex': fuzzy_regex,
                    'arglist': arglist,
                    'function': function,
                    'module': self.modules[-1]
                    })

            for regex, function in self.modules[-1].regexes:
                self.all_regexes.append((re.compile(regex), function, self.modules[-1]))

        for module in self.modules:
            module.network = self

            try:
                module.prefork()
            except AttributeError:
                pass

            module.setDaemon(True)
            module.start()





    def delegate(self, the_message):
        nick_blacklist = [n.lower() for n in self.conf.get('nick_blacklist')]

        try:
            module_blacklist = [m.lower() for m in self.conf.get('module_blacklist')[the_message.source]]
        except KeyError:
            module_blacklist = []

        if the_message.content.startswith(self.conf.get('comchar')):

            commands = get_possible_commands(the_message.content[len(self.conf.get('comchar')):].rstrip(), self.all_commands, module_blacklist=module_blacklist)
            ambiguity = len(commands)

            if ambiguity == 1:
                command_dict = commands[0]
                command_dict['args']['_command'] = command_dict['command']
                command_dict['module'].queue.put((command_dict['function'], the_message, command_dict['args']))

            elif ambiguity > 1:
                self.irc.privmsg(the_message.source, '\x02ambiguous command\x02\x03# |\x03 %s' % '\x03# :\x03 '.join(
                    [self.conf.get('comchar')+c['command'].replace('>>', '>').replace('<<', '<') for c in commands])
                    )

        for regex, function, module in self.all_regexes:
            match = regex.match(the_message.content)

            if match:
                if module.name.lower() not in module_blacklist and the_message.nick.lower() not in self.conf.get('nick_blacklist'):
                    module.queue.put((function, the_message, match))


    def dispatch(self, data):
        """ Deals with messages and sends modules the information they need. """
        if data == None:
            print ' :: no data'
            return None

        if data == '':
            print ' :: empty response, assuming disconnection\a' # alert
            sys.exit()

        for line in [line for line in data.split('\r\n') if len(line) > 0]:
            print '    %s' % line

            if line.startswith(':%s!%s@' % (self.conf.get('nick'), self.conf.get('username'))):
                self.irc.own_hostname = line.split(' ')[0][1:]
                print ' -- we are %s' % self.irc.own_hostname

            if line.startswith('PING :'):
                self.irc.pong(line)

            the_message = message.Message(line, self.irc.charset)

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

            elif the_message.type == 'INVITE':
                channel = the_message.content
                self.irc.join(channel)

            elif the_message.type == 'KICK':
                channel = the_message.content
                self.irc.part(channel)

            elif the_message.type == 'NOTICE':
                pass

            elif the_message.type == 'NICK':
                pass

            elif the_message.type == 'MODE' and self.initial == True:
                for channel in self.conf.get('network_channels'):
                    self.irc.join(channel)

                self.initial = False

            elif the_message.type == 'MODE':
                self.irc.getmode(line.split(' ')[2])

            elif the_message.type == 'PRIVMSG':
                self.delegate(the_message)
