import message

import sys
import thread

class Network(object):
    def __init__(self, conf, irc):
        self.conf = conf
        self.irc = irc
        self.modules = []

        for modulename in conf.get('modules'):
            __import__('modules.'+modulename)
            module = sys.modules['modules.'+modulename]
            setattr(module.Module, 'name', modulename)
            self.modules.append(module.Module(self.irc, conf))

            self.modules[-1].setDaemon(True)
            self.modules[-1].start()

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

            elif type == 'KICK':
                channel = message.content(line)
                self.irc.part(channel)

            elif type == 'NOTICE':
                pass

            elif type == 'NICK':
                pass

            elif type == 'PRIVMSG':
                for module in self.modules:
                    try:
                        blacklist = self.conf.get('module_blacklist')[module.name]
                    except KeyError:
                        module.queue.put(the_message)
                    else:
                        if the_message.source not in blacklist:
                            module.queue.put(the_message)
