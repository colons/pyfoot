from os import path
from random import choice
import parser

def extract(source, conf):
    """ Opens file and returns a random item from it """
    filename = path.expanduser(conf.get('content_dir'))+source+'.txt'
    file = open(filename)
    line_list = []
    for line in file:
        line_list.append(line)
    return choice(line_list)

class Module:
    def act(self, message, irc, conf):
        """ Sends random lines from arbitrary text files, as specified in the config file. """
        sources = conf.get('rantext_sources').split(',')
        for source in sources:
            if parser.args(message.content, source, conf) != False:
                line = extract(source, conf)
                irc.send(message.source, line)

