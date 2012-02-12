import re
import time

class Module:
    def __init__(self):
        self.woof = 'woof'

    def act(self, message, irc, conf):
        if re.compile(conf.get('woof_trigger'), re.IGNORECASE).search(message.content):
            irc.send(message.source, self.woof)
