import metamodule
import parser
import http_helper
import requests
import lxml.html

class Module(metamodule.MetaModule):
    def act(self, message):
        command = parser.args(message.content, 'surreal', self.conf)

        if command == True:
            page = requests.get('http://www.ravenblack.net/cgi-bin/surreal.cgi', headers={'User-Agent': http_helper.choose_agent()})
            content = lxml.html.fromstring(page.text).text_content().split('\n')[1]
            self.irc.send(message.source, content.encode("utf-8"))
