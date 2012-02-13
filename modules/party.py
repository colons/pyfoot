import parser
import urllib
import time
import codecs
from BeautifulSoup import BeautifulStoneSoup
from os import path
import re

def translate(source, target, phrase, conf):
    """ Translates phrase from source language to target language with Google's translation API """
    query = urllib.quote(phrase)
    page = urllib.urlopen('http://api.microsofttranslator.com/V2/Ajax.svc/Translate?appId=%s&from=%s&to=%s&text=%s' % (conf.get('bing_app_id'), source, target, query))
    result = page.read()
    print result
    return result


def dupes(party):
    """ Returns True if any phrase appears twice in our party """
    if ''.join(party[-1:]) in party[:-1]:
        return True
    else:
        return False

class Module:
    def act(self, message, irc, conf):
        """ A recreation of translationparty, only with better duplicate detection """
        initial_phrase = parser.args(message.content, 'party ', conf)
        if initial_phrase != False:
            party = [initial_phrase]
            while dupes (party) == False:
                party.append(translate('en', conf.get('transvia'), party[-1], conf))
                party.append(translate(conf.get('transvia'), 'en', party[-1], conf))
            
            filename = '%s-%s.txt' % (message.nick, time.strftime('%y%m%d-%H%M%S'))
            filepath = path.expanduser(conf.get('web_directory')+'party/'+filename)

            print 'Writing to %s...' % filepath
            file = codecs.open(filepath, mode='w')
            file.write('\n'.join(party))
            file.close()
            
            attempts = len(party)/2
            irc.send(message.source, '%s | \x02%i\x02 attempts | %sparty/%s' % (party[-1], attempts, conf.get('web_url'), filename))
