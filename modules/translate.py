import urllib
import time
import codecs
from BeautifulSoup import BeautifulStoneSoup
from os import path
import re

import parser
import metamodule



class Module(metamodule.MetaModule):
    def act(self, message, irc, conf):
        helpstring = "!translate <from> <to> <phrase>, where <from> and <to> are two-letter language codes"

        post_args = parser.args(message.content, 't ', conf)
        if len(post_args.split()) >= 3:
            source = post_args.split()[0]
            target = post_args.split()[1]
            phrase = ' '.join(post_args.split()[2:])
            irc.send(message.source, self.translate(source, target, phrase))
        elif len(post_args.split()) < 3:
            irc.send(message.source, helpstring)
