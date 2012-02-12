import parser
import urllib
import time
import codecs
from BeautifulSoup import BeautifulStoneSoup
from os import path

def translate(source, target, phrase, conf):
    """ Translates phrase from source language to target language with Google's translation API """
    query = urllib.quote(phrase)
    page = urllib.urlopen('https://www.googleapis.com/language/translate/v2?key=%s&q=%s&source=%s&target=%s' % (conf.get('google_api_key'), query, source, target))
    result = page.read().split("\"translatedText\": \"")[1].split("\"\n")[0]
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
            
            cleanparty = []
            for item in party:
                cleanitem = unicode(BeautifulStoneSoup(item, convertEntities=BeautifulStoneSoup.HTML_ENTITIES).contents[0])
                cleanparty.append(cleanitem)

            filename = '%s-%s.txt' % (message.nick, time.ctime().replace(' ', '-'))
            filepath = path.expanduser(conf.get('web_directory')+'party/'+filename)

            print 'Writing to %s...' % filepath
            file = codecs.open(filepath, encoding='utf-8', mode='w')
            file.write('\n'.join(cleanparty))
            file.close()
            
            attempts = len(party)/2
            irc.send(message.source, 'succeeded after %i attempts, see %sparty/%s' % (attempts, conf.get('web_url'), filename))
            irc.send(message.source, ''.join(party[-1]))
