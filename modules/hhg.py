from os import path
import parser
from random import choice
import re

def act(message, irc, conf):
    """ Picks a random line from <dir>/hhg.txt. If specified, limits the selection to lines spoken by a particular character. """

    character = parser.args(message.content, 'hhg', conf)
    
    if character != False:
        character = character.strip()
        hhg = open(path.expanduser(conf.get('content_dir')+'hhg.txt'))
        linelist = []

        if character == '':
            for line in hhg:
                if line.find(':') != -1:
                    quote = ''.join(line.split(':')[1:])
                    linelist.append(quote)

            irc.send(message.source, choice(linelist))
                
        else:
            match = re.compile('^%s' % character, re.IGNORECASE)
            for line in hhg:
                if match.search(line):
                    quote = ''.join(line.split(':')[1:])
                    linelist.append(quote)

            irc.send(message.source, choice(linelist))

