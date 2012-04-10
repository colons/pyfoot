import urllib2
import json
from random import choice
from math import fabs
from os import path
import pickle
import re

import parser
import metamodule

class Module(metamodule.MetaModule):
    """ fresh MyAnimeList facts, milled from the mal-api.com api """
    def __init__(self, irc, conf):
        metamodule.MetaModule.__init__(self, irc, conf)
        self.url = 'http://mal-api.com/%s?%s'
        self.default_args = ['format=json']
        self.user_file_path = path.expanduser(conf.get('content_dir')+'mal')
        self.malusers = {}
        self.help_setup = "link a MyAnimeList account to your IRC nick with '"+conf.get('comchar')+"mal set <account name>'"
        self.help_missing = 'no such MAL user \x02%s\x02'
        
        try:
            userfile = open(self.user_file_path)
            self.malusers = pickle.load(userfile)
            userfile.close()
        except:
            print ' :: error reading MAL user pickle, will create one when necessary'
    
    
    def maluser(self, user):
        """ Takes a user - irc or mal - and determines the appropriate MAL username """
        try:
            maluser = self.malusers[self.conf.get('address')+' '+user.lower()]
        except KeyError:
            return user
        else:
            return maluser


    def select(self, things, limit=5):
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
    
    
    def oiz(self, thing):
        if thing == 0:
            return '-'
        else:
            return thing


    def summarise_user(self, user):
        user = self.maluser(user)
        try:
            data = self.query('animelist/%s' % user)
        except urllib2.HTTPError:
            return self.help_missing % user
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

        summary = 'http://myanimelist.net/animelist/\x02%s\x02 | \x02%s\x02 days across \x02%d\x02 shows | %s' % (user, days, len(consumed),
                ' | '.join(['%s : \x02%s\x02/\x02%s\x02 : \x02%s\x02' % (a['title'], self.oiz(a['watched_episodes']),
                    self.oiz(a['episodes']), self.oiz(a['score'])) for a in selection]))
        return summary
    
    def common_shows(self, users):
        """ Get a list of tuples of shows that any two users have in common """
        ud_list = []
        for user in users:
            try:
                data = self.query('animelist/%s' % user)
            except urllib2.HTTPError:
                return self.help_missing % user
            ud_list.append(data)
        
        common = []

        for a1 in ud_list[0]['anime']:
            for a2 in ud_list[1]['anime']:
                if a1['id'] == a2['id'] and a1['watched_status'] != 'plan to watch' and a2['watched_status'] != 'plan to watch':
                    common.append((a1, a2))

        return common


    def compare_users(self, users):
        users = [self.maluser(u) for u in users]
        common = self.common_shows(users)
        if type(common) == str:
            return common

        total_score_diff = 0
        consensus = [] # animes scored the same
        both_scored = 0
        
        for a1, a2 in common:
            if (a1['score'] == a2['score']) and a1['score'] != 0:
                consensus.append(a1)
            if a1['score'] != 0 and a2['score'] != 0:
                both_scored += 1

        
        if len(consensus) > 0:
            selection = self.select(consensus)
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
                selection = self.select(closest)
                return "\x02%s\x02 and \x02%s\x02 | \x02%d\x02 common shows | %s" % (
                        users[0], users[1], len(common),
                        ' | '.join(['%s : \x02%d\x02, \x02%d\x02' % (a[0]['title'], a[0]['score'], a[1]['score']) for a in selection]))
            else:
                # we have no common ground :<
                selection = self.select(common)
                return "\x02%s\x02 and \x02%s\x02 have \x02%d\x02 shows in common | %s" % (users[0], users[1],
                        len(common), ' | '.join([a[0]['title'] for a in selection]))


    def fight(self, users):
        users = [self.maluser(u) for u in users]
        common = self.common_shows(users)
        if type(common) == str:
            return common
        
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
            selection = self.select(contention)
            return "\x02%s\x02 vs. \x02%s\x02 | average contention : \x02%.2f\x02 | %s" % (
                    users[0], users[1], average_gap,
                    ' | '. join(['%s : \x02%d\x02 vs. \x02%d\x02' % (a[0]['title'], a[0]['score'], a[1]['score']) for a in selection]))
        else:
            return "\x02%s\x02 and \x02%s\x02 need to watch and score more stuff" % (users[0], users[1])

    def search(self, query):
        search = self.query('anime/search', ['q=%s' % urllib2.quote(query)])

        # data = self.query('anime/%i' % search[0]['id'])
        try:
            data = search[0]
        except IndexError:
            return 'no results | http://myanimelist.net/anime.php?q=%s' % urllib2.quote(query)
        
        showpage = 'http://myanimelist.net/anime/%i' % search[0]['id']
        
        # the html stripping should not be here, but it is for now because fuck you
        return '\x02%s\x02 : %s | %s | %s' % (data['title'], data['type'], showpage, re.sub('<[^<]+?>', '', data['synopsis']))

    def testauth(self):
        pass


    def query(self, query, additional_args=[]):
        args = '&'.join(self.default_args+additional_args)
        print self.url % (query, args)
        data = json.load(urllib2.urlopen(self.url % (query, args)))
        return data


    def act(self, message):
        post_arg = parser.args(message.content, 'mal', self.conf)
        
        if post_arg == False:
            return

        if post_arg == True:
            try:
                maluser = self.malusers[self.conf.get('address')+' '+message.nick.lower()]
            except KeyError:
                self.irc.send(message.source, self.help_setup, pretty=True)
            else:
                self.irc.send(message.source, self.summarise_user(message.nick), pretty=True)

        elif post_arg.split()[0] == 'compare' and len(post_arg.split()) == 3:
            # what are these two people like?
            users = post_arg.split()[1:]
            self.irc.send(message.source, self.compare_users(users), pretty=True)

        elif post_arg.split()[0] == 'compare' and len(post_arg.split()) == 2:
            # what are we like?
            try:
                maluser = self.malusers[self.conf.get('address')+' '+message.nick]
            except KeyError:
                self.irc.send(message.source, self.help_setup, pretty=True)
            else:
                users = [message.nick, post_arg.split()[1]]
                self.irc.send(message.source, self.compare_users(users), pretty=True)

        elif post_arg.split()[0] in ['battle', 'fight', 'argue'] and len(post_arg.split()) == 3:
            # a fight with both parties specified
            users = post_arg.split()[1:]
            self.irc.send(message.source, self.fight(users), pretty=True)

        elif post_arg.split()[0] in ['battle', 'fight', 'argue'] and len(post_arg.split()) == 2:
            # a fight with one party issuing the challenge
            try:
                maluser = self.malusers[self.conf.get('address')+' '+message.nick]
            except KeyError:
                self.irc.send(message.source, self.help_setup, pretty=True)
            else:
                users = [message.nick, post_arg.split()[1]]
                self.irc.send(message.source, self.fight(users), pretty=True)

        elif post_arg.split()[0] in ['set', 'iam', "i'm"] and len(post_arg.split()) == 2:
            # a user is telling us who they are
            try:
                data = self.query('animelist/%s' % post_arg.split()[1])
            except urllib2.HTTPError:
                self.irc.send(message.source, self.help_missing % post_arg.split()[1], pretty=True)
            else:
                try: # just in case other instances of pyfoot have altered the file since we last read it
                    userfile = open(self.user_file_path)
                    self.malusers = pickle.load(userfile)
                    userfile.close()
                except:
                    print ' :: error reading MAL user pickle, creating one now'

                self.malusers[self.conf.get('address')+' '+message.nick.lower()] = post_arg.split()[1]
                userfile = open(self.user_file_path, 'w')
                pickle.dump(self.malusers, userfile)
                userfile.close()
                self.irc.send(message.source, '\x02%s\x02 is MAL user \x02%s\x02' % (message.nick, post_arg.split()[1]), pretty=True)

        elif post_arg.split()[0] in ['search', 's', 'find', 'f'] and len(post_arg.split()) > 1:
            self.irc.send(message.source, self.search(' '.join(post_arg.split()[1:])), pretty=True, crop=True)

        elif len(post_arg.split()) == 1:
            user = post_arg.split()[0]
            print user
            self.irc.send(message.source, self.summarise_user(user), pretty=True)

    def correlate(self, id1, id2):
        print 'hi'
