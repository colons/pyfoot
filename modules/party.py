import urllib
import time
import codecs
from BeautifulSoup import BeautifulStoneSoup
from os import path
import re

import parser
import metamodule

def dupes(party):
    """ Returns True if any phrase appears twice in our party """
    if ''.join(party[-1:]) in party[:-1]:
        return True
    else:
        return False

class Module(metamodule.MetaModule):
    def act(self, message):
        """ A recreation of translationparty, only with better duplicate detection """
        initial_phrase = parser.args(message.content, 'party', self.conf)

        if initial_phrase == False:
            return

        if len(initial_phrase) != 0:
            party = [initial_phrase]
            while dupes (party) == False:
                party.append(self.translate('en', self.conf.get('transvia'), party[-1]))
                party.append(self.translate(self.conf.get('transvia'), 'en', party[-1]))
            
            filename = '%s-%s.txt' % (message.nick, time.strftime('%y%m%d-%H%M%S'))
            filepath = path.expanduser(self.conf.get('web_directory')+'party/'+filename)

            print 'Writing to %s...' % filepath
            file = codecs.open(filepath, mode='w')
            file.write('\n'.join(party))
            file.close()
            
            attempts = len(party)/2
            self.irc.send(message.source, '%s | \x02%i\x02 attempts | %sparty/%s' % (party[-1], attempts, self.conf.get('web_url'), filename))
