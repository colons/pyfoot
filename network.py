import message

import sys
import thread

class Network(object):
    def __init__(self, conf, irc):
        self.conf = conf
        self.irc = irc
        self.modules = []
        self.commands = {}

        for modulename in conf.get('modules'):
            __import__('modules.'+modulename)
            module = sys.modules['modules.'+modulename]
            # setattr(module.Module, 'name', modulename)
            self.modules.append(module.Module(self.irc, conf))

            self.commands.update(self.modules[-1].get_commands())

    def dispatch(self, data):
        """ Deals with messages and sends modules the information they need. """
        if data == None:
            print ' :: no data'
            return None
        
        if data == '':
            print ' :: empty response, assuming disconnection\a' # alert
            self.irc.close()

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
                
            if type == '324':
                # this is a list of channel modes
                splitline = line.split(' ')
                name = splitline[3]
                modelist = splitline[4]

            elif type == 'INVITE':
                channel = message.content(line)
                self.irc.join(channel)

            elif type == 'NOTICE':
                pass

            elif type == 'NICK':
                pass

            elif type == 'PRIVMSG':
                for command in self.commands:
                    print '%s%s' % (self.conf.get('comchar'), command)
            
                    if the_message.content.startswith('%s%s' % (self.conf.get('comchar'), command)):
                        print 'match!'
                        self.commands[command](the_message)
