import json
import urllib2

import module

class Module(module.Module):
    def prepare(self):
        self.url = 'http://api.duckduckgo.com/?q=%s&format=json&no_redirect=1&no_html=1&skip_disambig=1'
        self.frame = '\x02%s\x02 : %s'

    def register_commands(self):
        self.commands = [
                ('ddg <query>', self.ddg)
                ]

    def query(self, query):
        # response = urllib2.urlopen(self.url % query, None, {'User-Agent': 'pyfoot/hg bitbucket.org/colons/pyfoot/'})
        response = urllib2.urlopen(self.url % query)
        data = json.load(response)
        return data
    
    def get_answer(self, query):
        data = self.query(query)
        print data['Answer']
        if data['Answer'] == "Safe search filtered your search to: <b>off</b>. Use !safeoff command to turn off temporarily.":
            return "sorry, duckduckgo can't deal with dirty words, the pussies"

        if data['Redirect']:
            return data['Redirect']
        
        if data['Answer']:
            return self.frame % (data['AnswerType'], data['Answer'])

        if data['AbstractText']:
            return self.frame % (data['AbstractText'], data['AbstractURL'])

        if data['Definition']:
            return self.frame % (': '.join(data['Definition'].split(': ')[1:]), data['DefinitionURL'])

        if len(data['RelatedTopics']) == 1:
            return self.frame % (data['RelatedTopics'][0]['Text'], data['RelatedTopics'][0]['FirstURL'])
        
        if len(data['RelatedTopics']) > 1:
            return self.frame+' |  %i other topics' % (data['RelatedTopics'][0]['Text'], data['RelatedTopics'][0]['FirstURL'], len(data['RelatedTopics']))

        return 'search'

    def ddg(self, message):
        """ Issue a <a href="http://duckduckgo.com/api.html">DuckDuckGo</a> query.
        $<comchar>ddg 2^10
        >\x02calc\x02\x034 :\x03 2 ^ 10 = 1,024\x034 |\x03 http://ddg.gg/?q=2%5E10 """
        post_arg = parser.args(message.content, 'ddg', self.conf)
        if post_arg != False and len(post_arg) != 0:
            query = urllib2.quote(post_arg)
            answer = self.get_answer(query)
            if answer:
                self.irc.send(message.source, '%s | http://ddg.gg/?q=%s' % (answer, query), pretty=True)
