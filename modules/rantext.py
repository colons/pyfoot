from random import choice

import module


class Module(module.Module):
    """ Retrieve a random line from a text file. Can be directed at individuals. """
    def prepare(self):
        self.sources = {}
        for source in self.conf.get('rantext_sources'):
            filename = self.conf.get('content_dir')+source+'.txt'
            file = open(filename)
            line_list = []
            for line in file:
                line_list.append(line)
            self.sources[source] = line_list

    def register_commands(self):
        self.commands = []
        for source in self.conf.get('rantext_sources'):
            everyone_func = lambda message, args: self.do_a_thing(message, args)
            everyone_func.__doc__ = '$<comchar>%s\n>%s' % (source, self.extract(source))

            targetted_func = lambda message, args: self.do_a_thing(message, args)

            self.commands.append((source, everyone_func))
            self.commands.append(('%s <nick>' % source, targetted_func))

    def do_a_thing(self, message, args):
        source = message.content[len(self.conf.get('comchar')):].split(' ')[0]

        line = self.extract(source)

        if 'nick' in args:
            line = '%s: %s' % (args['nick'], line)

        self.irc.send(message.source, line)
    
    def extract(self, source):
        """ Opens file and returns a random item from it """
        return choice(self.sources[source])
