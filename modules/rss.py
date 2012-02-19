import thread
from time import sleep
import feedparser

import parser
import metamodule

class Module(metamodule.MetaModule):
    """ An RSS reader, and the first pyfoot module that posts without act() """
    def __init__(self, irc, conf):
        metamodule.MetaModule.__init__(self, irc, conf)
        
        self.latestitem = {}

        for i in self.conf.get('rss').split(','):
            # get latest item, remember to ignore it
            channel, url = i.split()
            try:
                feed = feedparser.parse(url)
                self.latestitem[url] = feed['items'][0]
            except:
                pass

        thread.start_new_thread(self.loop, ())

    def loop(self):
        while True:
            sleep(150)

            for i in self.conf.get('rss').split(','):
                channel, url = i.split()
                try:
                    feed = feedparser.parse(url)
                    item = feed['items'][0] 
                except:
                    pass
                else:
                    if item['link'] != self.latestitem[url]['link']:
                        self.latestitem[url] = feed['items'][0]
                        title = self.latestitem['title']
                        link = self.latestitem['link']
                    
                        self.irc.send(channel, '%s | %s' % (title, link))
