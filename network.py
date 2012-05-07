import message

import sys
import thread
import re

def get_possible_commands(content, commands):
    """ Return a list of matching command descriptions. """
    possible_commands = []
    print content
    
    for command, regex, arglist, function, module in commands:
        args = {}

        match = regex.match(content)
        if match:
            i = 1
            for arg in arglist:
                args[arg] = match.group(i)
                i += 1

            possible_commands.append((command, module, function, args))

    return possible_commands


def command_to_regex_and_arglist(command, loose=False):
    """ Take a command and return a regex and a list of arguments. ignore_variables if you're help.py """
    regex = ''
    arglist = []

    for word in command.split(' '):
        arg = re.match('<(\S+)>$', word)

        if arg:
            if loose:
                pass
            elif re.match('<<(\S+)>>$', word):
                arglist.append(arg.group(1)[1:-1])
                regex += '(.+)\s+'
            else:
                arglist.append(arg.group(1))
                regex += '(\S+)\s+'
        else:
            regex += word[0]

            for letter in word[1:]:
                regex += '(?:\\b|[%s]' % letter
            for letter in word[1:]:
                regex += ')'

            regex += '\s+'

    
    regex = regex[:-3]

    if not loose:
        regex += '$'

    compiled_regex = re.compile(regex)

    return compiled_regex, arglist


class Network(object):
    def __init__(self, conf, irc):
        self.initial = True
        self.conf = conf
        self.irc = irc
        self.irc = irc
        self.modules = []
        self.all_commands = []
        self.all_regexes = []

        for modulename in conf.get('modules'):
            __import__('modules.'+modulename)
            module = sys.modules['modules.'+modulename]
            setattr(module.Module, 'name', modulename)
            self.modules.append(module.Module(self.irc, conf))

            for command, function in self.modules[-1].commands:
                regex, arglist = command_to_regex_and_arglist(command)
                self.all_commands.append((command, regex, arglist, function, self.modules[-1]))

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
        
        if the_message.content.startswith(self.conf.get('comchar')):
            commands = get_possible_commands(the_message.content[len(self.conf.get('comchar')):].rstrip(), self.all_commands)
            ambiguity = len(commands)

            if ambiguity == 1:
                command, module, function, args = commands[0]
                args['_command'] = command
                module.queue.put((function, the_message, args))

            elif ambiguity > 1:
                self.irc.send(the_message.source, '\x02ambiguous command\x02\x034 |\x03 %s' % '\x034 :\x03 '.join(
                    [self.conf.get('comchar')+c[0].replace('>>', '>').replace('<<', '<') for c in commands])
                    )

        
        for regex, function, module in self.all_regexes:
            match = regex.match(the_message.content)

            if match:
                try:
                    module_blacklist = [c.lower() for c in self.conf.get('module_blacklist')[module.name]]
                except KeyError:
                    module_blacklist = []
                
                if the_message.source.lower() not in module_blacklist and the_message.nick.lower() not in self.conf.get('nick_blacklist'):
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

            if line.startswith('PING :'):
                self.irc.pong(line)
            
            try:
                type = ''.join(line.split(':')[:2]).split(' ')[1]
            except(IndexError):
                type = None
            else:
                the_message = message.Message(line)
                
            if type == '353':
                # this is a channel names list
                pass

            if type == '324':
                # this is a list of channel modes
                splitline = line.split(' ')
                name = splitline[3]
                modelist = splitline[4]
                try:
                    self.irc.channels[name]['modes'] = modelist
                except KeyError:
                    self.irc.channels[name] = {}
                    self.irc.channels[name]['modes'] = modelist

            elif type == 'INVITE':
                channel = the_message.content
                self.irc.join(channel)

            elif type == 'KICK':
                channel = the_message.content
                self.irc.part(channel)

            elif type == 'NOTICE':
                pass

            elif type == 'NICK':
                pass

            elif type == 'MODE' and self.initial == True:
                for channel in self.conf.get('network_channels'):
                    self.irc.join(channel)

                self.initial = False

            elif type == 'PRIVMSG':
                self.delegate(the_message)
