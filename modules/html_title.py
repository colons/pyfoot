import BeautifulSoup
import urllib
from urlparse import urlparse
import string
import http_helper
from random import choice
import re

import metamodule

class Module(metamodule.MetaModule):
    def act(self, message):
        for word in message.content.split():
            if word.startswith('http://') or word.startswith('https://'):
                permitted = True

                for i in self.conf.get('url_blacklist').split(','):
                    channel, blacklist = i.split(' ')

                    if channel == message.source and re.match(blacklist, word):
                        permitted = False

                if permitted:

                    '''AJAX HTML Snapshot URL parsing'''
                    hashbang_index = word.find('#!')
                    if hashbang_index != -1:
                        url_base = word[:hashbang_index]
                        if '?' in url_base:
                            join = '&'
                        else:
                            join = '?'
                        url_fragment = urllib.quote(word[hashbang_index+2:], '=')
                        word = url_base + join + '_escaped_fragment_=' + url_fragment

                    parsed_url = urlparse(word)

                    opener = urllib.FancyURLopener()
                    setattr(opener, 'version', choice(http_helper.user_agents))

                    try:
                        pagesoup = BeautifulSoup.BeautifulSoup(opener.open(word))
                        title = BeautifulSoup.BeautifulStoneSoup((pagesoup.title.string).replace('\n', '').strip(), convertEntities="html").contents[0]
                        summary = '%s\x034 |\x03\x02 %s\x02' % (title, parsed_url.hostname)
                        self.irc.send(message.source, summary)
                    except AttributeError:
                        pass
                    except IOError as (errno, strerror):
                        #if errno == 'socket error':
                            #if strerror.find('-2') != -1:
                            #if strerror.error == -2:
                                #self.irc.send(message.source, "Errorno %s: %s:\x02 %s\x02" % (errno, strerror, parsed_url.hostname))
                        pass
