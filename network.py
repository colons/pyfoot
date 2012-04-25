from irc import IRC
import parser
import sys
import ConfigParser

class Network(object):
    """ The whole network! This class takes a config object as an argument and uses it to set up our connection and then run the loop """
    def __init__(self, conf):
        """ Get configuration shit and connect and set everything up """
        self.modules = []

        self.irc = IRC(conf.get('address'), conf.get('port'), conf.get('nick'), conf.get('username'), conf.get('hostname'), conf.get('servername'), conf.get('realname'), ssl_enabled=bool(conf.get('ssl')))

        for modulename in conf.get('modules').split(','):
            __import__('modules.'+modulename)
            module = sys.modules['modules.'+modulename]
            setattr(module.Module, 'name', modulename)
            self.modules.append(module.Module(self.irc, conf))

        try:
            while True:
                """ Here's where the shit happens """
                data = self.irc.listen()
                print data,

                parser.dispatch(data, self.irc, self.modules, conf)
        except KeyboardInterrupt:
            print '^C pressed, exiting.'
        finally:
            try:
                cause_of_death = conf.get('quit_message')
            except ConfigParser.NoOptionError:
                cause_of_death = 'Leaving!'
            self.irc.close(cause_of_death)
