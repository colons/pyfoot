import urllib2
import json
from random import choice

import parser


class Module:
    """ fresh MyAnimeList facts, milled from the mal-api.com api """
    def __init__(self):
        self.url = 'http://mal-api.com/%s?format=json'

        # the number of items to cap printed lists at
        self.limit = 10

    def act(self, message, irc, conf):
        post_arg = parser.args(message.content, 'mal ', conf)
        if post_arg and post_arg.split()[0] == 'compare' and len(post_arg.split()) == 3:
            users = post_arg.split()[1:]
            irc.send(message.source, self.compare_users(users))
        elif post_arg and len(post_arg.split()) > 0:
            print post_arg
            user = post_arg.split()[0]
            irc.send(message.source, self.summarise_user(user))


    def select(self, things):
        # selection = sorted(animelist, key=lambda anime: anime['score'], reverse=True)[:self.limit]
        if len(things) <= self.limit:
            selection = things
        else:
            selection = []
            
            while len(selection) < self.limit:
                thing = choice(things)
                if thing not in selection:
                    selection.append(thing)
        
        return selection


    def summarise_user(self, user):
        data = self.query('animelist/%s' % user)
        days = data['statistics']['days']
        animelist = data['anime']
        
        consumed = []
        planned = 0

        for a in animelist:
            if a['watched_status'] == 'plan to watch':
                planned += 1
            else:
                consumed.append(a)
        
        selection = self.select(consumed)

        summary = '%s :: %s days across %d shows :: %s' % (user, days, len(consumed), ', '.join([a['title'] for a in selection]))
        return summary

            
    def compare_users(self, users):
        # user data list
        ud_list = []
        for user in users:
            data = self.query('animelist/%s' % user)
            ud_list.append(data)
        
        # let's always use the shortest list for our comparisons, shall we?
        # not that it makes a difference
        ud_list = sorted(ud_list, key=lambda x: len(x['anime']))
        
        common = []

        for a1 in ud_list[0]['anime']:
            for a2 in ud_list[1]['anime']:
                if a1['id'] == a2['id'] and a1['watched_status'] != 'plan to watch' and a2['watched_status'] != 'plan to watch':
                    common.append((a1, a2))

        print [a[0]['title'] for a in common]

        total_score_diff = 0
        consensus = [] # animes scored the same
        
        for a1, a2 in common:
            if (a1['score'] == a2['score']) and a1['score'] != 0:
                print a1['title']
                consensus.append(a1)

        selection = self.select(consensus)
        
        return '%s and %s agree about %d/%d common shows :: %s' % (users[0], users[1], len(consensus), len(common), ', '.join(['%s (%d)' % (a['title'], a['score']) for a in selection]))


    def testauth(self):
        pass


    def query(self, query):
        data = json.load(urllib2.urlopen(self.url % query))
        return data
