from os import path
import parser
from random import choice
import re

import metamodule

class Module(metamodule.MetaModule):
    def act(self, message):
        """ Picks a random line from <dir>/hhg.txt. If specified, limits the selection to lines spoken by a particular character. """

        character = parser.args(message.content, 'hhg', self.conf)
        
        if character != False:
            hhg = open(path.expanduser(self.conf.get('content_dir')+'hhg.txt'))
            linelist = []

            if character == True:
                for line in hhg:
                    if line.find(':') != -1:
                        quote = ''.join(line.split(':')[1:])
                        linelist.append(quote)

            else:
                character = character.strip()
                        
                match = re.compile('^%s' % character, re.IGNORECASE)
                for line in hhg:
                    if match.search(line):
                        quote = ''.join(line.split(':')[1:])
                        linelist.append(quote)

            self.irc.send(message.source, choice(linelist))
