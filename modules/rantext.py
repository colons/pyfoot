from os import path
from random import choice

import parser
import metamodule

def extract(source, conf):
    """ Opens file and returns a random item from it """
    filename = path.expanduser(conf.get('content_dir'))+source+'.txt'
    file = open(filename)
    line_list = []
    for line in file:
        line_list.append(line)
    return choice(line_list)

class Module(metamodule.MetaModule):
    def act(self, message):
        """ Sends random lines from arbitrary text files, as specified in the config file. """
        sources = self.conf.get('rantext_sources').split(',')
        for source in sources:
            if parser.args(message.content, source, self.conf) != False:
                line = extract(source, self.conf)
                self.irc.send(message.source, line)

