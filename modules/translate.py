import urllib
import time
import codecs
from BeautifulSoup import BeautifulStoneSoup
from os import path
import re

import parser
import metamodule



class Module(metamodule.MetaModule):
    def __init__(self, irc, conf):
        metamodule.MetaModule.__init__(self, irc, conf)
        self.helpstring = "!translate <from> <to> <phrase>, where <from> and <to> are two-letter language codes"

    def act(self, message):
        post_args = parser.args(message.content, ['t', 'tr', 'trans', 'translate'], self.conf)

        if post_args == False:
            return

        if len(post_args.split()) >= 3:
            source = post_args.split()[0]
            target = post_args.split()[1]
            phrase = ' '.join(post_args.split()[2:])
            translation = self.translate(source, target, phrase)
            self.irc.send(message.source, translation)

        elif len(post_args.split()) < 3:
            self.irc.send(message.source, self.helpstring)
