import BeautifulSoup
import urllib
from urlparse import urlparse
import string
from random import choice
import re

import metamodule

class Module(metamodule.MetaModule):
    def __init__(self, irc, conf):
        metamodule.MetaModule.__init__(self, irc, conf)
        self.user_agents = [
            'Mozilla/5.0 (Windows; U; Windows NT 5.1; it; rv:1.8.1.11) Gecko/20071127 Firefox/2.0.0.11',
            'Opera/9.25 (Windows NT 5.1; U; en)',
            'Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; .NET CLR 1.1.4322; .NET CLR 2.0.50727)',
            'Mozilla/5.0 (compatible; Konqueror/3.5; Linux) KHTML/3.5.5 (like Gecko) (Kubuntu)',
            'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.8.0.12) Gecko/20070731 Ubuntu/dapper-security Firefox/1.5.0.12',
            'Lynx/2.8.5rel.1 libwww-FM/2.14 SSL-MM/1.4.1 GNUTLS/1.2.9'
        ]

    def act(self, message):
        for word in message.content.split():
            if word.startswith('http://') or word.startswith('https://'):
                permitted = True

                for i in self.conf.get('url_blacklist').split(','):
                    channel, blacklist = i.split(' ')

                    if channel == message.source and re.match(blacklist, word):
                        permitted = False

                    ''' TODO
                    > follow redirects
                    > and then have the domain printed
                    > be the domain you're eventually directed to
                    > extra credit: breadcrumb trail
                    > although that's totally unnecessary
                    > but it would be kinda cool '''

                if permitted:
                    hashbang = '#!'

                    #hashbang_index = word.find(hashbang)
                    #if hashbang_index != -1:
                    if hashbang in word:
                        word = string.replace(word, hashbang, '?_escaped_fragment_=')
                        #string.split(hashbang)[0]+hashbang+urllib.quote(str.split(hashbang)[1])

                    parsed_url = urlparse(word)

                    opener = urllib.FancyURLopener()
                    setattr(opener, 'version', choice(self.user_agents))

                    try:
                        pagesoup = BeautifulSoup.BeautifulSoup(opener.open(word))
                        title = BeautifulSoup.BeautifulStoneSoup((pagesoup.title.string).replace('\n', '').strip(), convertEntities="html").contents[0]
                        summary = '%s\x034 |\x03\x02 %s\x02' % (title, parsed_url.hostname)
                        self.irc.send(message.source, summary)
                    except AttributeError:
                        pass
                    except IOError:
                        pass


