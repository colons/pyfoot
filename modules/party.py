import parser
import urllib
import time
import codecs
from BeautifulSoup import BeautifulStoneSoup

def translate(source, target, phrase, conf):
    query = urllib.quote(phrase)
    page = urllib.urlopen('https://www.googleapis.com/language/translate/v2?key=%s&q=%s&source=%s&target=%s' % (conf.get('google_api_key'), query, source, target))
    result = page.read().split("\"translatedText\": \"")[1].split("\"\n")[0]
    print result
    print type(result)
    return result


def dupes(party):
    if ''.join(party[-1:]) in party[:-1]:
        return True
    else:
        return False

def act(message, irc, conf):
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
        file = codecs.open('%sparty/%s' % (conf.get('web_directory'), filename), encoding='utf-8', mode='w')
        file.write('\n'.join(cleanparty))
        file.close()
        attempts = len(party)/2
        irc.send(message.source, 'succeeded after %i attempts, see %sparty/%s' % (attempts, conf.get('web_url'), filename))
        irc.send(message.source, ''.join(party[-1]))
