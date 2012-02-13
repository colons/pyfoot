import urllib2
import json
from random import choice
from math import fabs

import parser


class Module:
    """ fresh MyAnimeList facts, milled from the mal-api.com api """
    def __init__(self):
        self.url = 'http://mal-api.com/%s?format=json'


    def act(self, message, irc, conf):
        post_arg = parser.args(message.content, 'mal ', conf)
        if post_arg and post_arg.split()[0] == 'compare' and len(post_arg.split()) == 3:
            users = post_arg.split()[1:]
            irc.send(message.source, self.compare_users(users))
        elif post_arg and post_arg.split()[0] in ['battle', 'fight', 'argue'] and len(post_arg.split()) == 3:
            users = post_arg.split()[1:]
            irc.send(message.source, self.fight(users))
        elif post_arg and len(post_arg.split()) > 0:
            user = post_arg.split()[0]
            irc.send(message.source, self.summarise_user(user))


    def select(self, things, limit=10):
        # selection = sorted(animelist, key=lambda anime: anime['score'], reverse=True)[:limit]
        if len(things) <= limit:
            selection = things
        else:
            selection = []
            
            while len(selection) < limit:
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

        summary = '\x02%s\x02 | \x02%s\x02 days across \x02%d\x02 shows | %s' % (user, days, len(consumed),
                ' | '.join([a['title'] for a in selection]))
        return summary
    
    def common_shows(self, users):
        """ Get a list of tuples of shows that any two users have in common """
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

        return common


    def compare_users(self, users):
        common = self.common_shows(users)

        total_score_diff = 0
        consensus = [] # animes scored the same
        both_scored = 0
        
        for a1, a2 in common:
            if (a1['score'] == a2['score']) and a1['score'] != 0:
                consensus.append(a1)
            if a1['score'] != 0 and a2['score'] != 0:
                both_scored += 1

        
        if len(consensus) > 0:
            selection = self.select(consensus, limit=7)
            return '\x02%s\x02 and \x02%s\x02 | \x02%d\x02 common shows | agreement on \x02%d\x02/\x02%d\x02 mutually scored shows | %s' % (
                    users[0], users[1], len(common), len(consensus), both_scored,
                    ' | '.join(['%s : \x02%d\x02' % (a['title'], a['score']) for a in selection]))
        else:
            # find the closest thing to common ground we have
            smallest_gap = 10
            closest = []

            for a1, a2 in common:
                if a1['score'] != 0 and a2['score'] != 0:
                    gap = fabs(a1['score'] - a2['score']) 
                    if gap < smallest_gap:
                        smallest_gap = gap
                        closest = [(a1, a2)]
                    elif gap == smallest_gap:
                        closest.append((a1, a2))
                
            if len(closest) > 0:
                selection = self.select(closest, limit=5)
                return "\x02%s\x02 and \x02%s\x02 | \x02%d\x02 common shows | %s" % (
                        users[0], users[1], len(common),
                        ' | '.join(['%s : \x02%d\x02, \x02%d\x02' % (a[0]['title'], a[0]['score'], a[1]['score']) for a in selection]))
            else:
                # we have no common ground :<
                selection = self.select(common)
                return "\x02%s\x02 and \x02%s\x02 have \x02%d\x02 shows in common | %s" % (users[0], users[1],
                        len(common), ' | '.join([a[0]['title'] for a in selection]))


    def fight(self, users):
        common = self.common_shows(users)
        
        largest_gap = 0
        contention = []
        total_gap = 0
        considered = 0

        for a1, a2 in common:
            if a1['score'] != 0 and a2['score'] != 0:
                gap = fabs(a1['score'] - a2['score']) 
                total_gap += gap
                considered += 1
                if gap > largest_gap:
                    largest_gap = gap
                    contention = [(a1, a2)]
                elif gap == largest_gap:
                    contention.append((a1, a2))
        
        if considered > 0:
            average_gap = total_gap/float(considered)

        if len(contention) > 0:
            selection = self.select(contention, limit=6)
            return "\x02%s\x02 vs. \x02%s\x02 | average contention : \x02%.2f\x02 | %s" % (
                    users[0], users[1], average_gap,
                    ' | '. join(['%s : \x02%d\x02 vs. \x02%d\x02' % (a[0]['title'], a[0]['score'], a[1]['score']) for a in selection]))
        else:
            return "\x02%s\x02 and \x02%s\x02 need to watch and score more stuff" % (users[0], users[1])


    def testauth(self):
        pass


    def query(self, query):
        data = json.load(urllib2.urlopen(self.url % query))
        return data
