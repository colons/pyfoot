import json
import urllib2

import metamodule
import parser

class Module(metamodule.MetaModule):
    """ a DuckDuckGo zero-click API frontend """
    def __init__(self, conf):
        self.url = 'http://api.duckduckgo.com/?q=%s&format=json&no_redirect=1&no_html=1&skip_disambig=1'

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
            return '%s | %s' % (data['AnswerType'], data['Answer'])

        if data['AbstractText']:
            return '%s | %s' % (data['AbstractText'], data['AbstractURL'])

        if data['Definition']:
            return '%s | %s' % (': '.join(data['Definition'].split(': ')[1:]), data['DefinitionURL'])

        if len(data['RelatedTopics']) > 0:
            return '%s | %s' % (data['RelatedTopics'][0]['Text'], data['RelatedTopics'][0]['URL'])
        
        return 'dunno, have some results i guess'

    def act(self, message, irc, conf):
        post_arg = parser.args(message.content, 'ddg ', conf)
        if post_arg:
            query = urllib2.quote(post_arg)
            answer = self.get_answer(query)
            if answer:
                irc.send(message.source, '%s | http://ddg.gg/?q=%s' % (answer, query))