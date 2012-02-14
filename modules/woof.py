import re
import time
import metamodule

class Module(metamodule.MetaModule):
    def __init__(self, conf):
        self.woof = conf.get('woof')

    def act(self, message, irc, conf):
        if re.compile(conf.get('woof_trigger'), re.IGNORECASE).search(message.content):
            irc.send(message.source, self.woof)
