import metamodule
import parser
import http_helper
import requests
import lxml.html
from random import choice
import re

class Module(metamodule.MetaModule):
    def act(self, message):
        command = parser.args(message.content, 'surreal', self.conf)

        if command == True:
            page = requests.get('http://www.ravenblack.net/cgi-bin/surreal.cgi', headers={'User-Agent': choice(http_helper.user_agents)})
            content = lxml.html.fromstring(page.text).text_content().split('\n')[1].encode("utf-8")
            self.irc.send(message.source, content)
