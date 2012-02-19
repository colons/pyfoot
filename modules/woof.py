import re
import time
import metamodule

class Module(metamodule.MetaModule):
    """ He's a dog, right? Get it? """
    def __init__(self, irc, conf):
        """ not really necessary, more a proof of concept than anything """
        metamodule.MetaModule.__init__(self, irc, conf)
        self.woof = self.conf.get('woof')
        self.regex = re.compile(self.conf.get('woof_trigger'), re.IGNORECASE)

    def act(self, message):
        if self.regex.search(message.content):
            self.irc.send(message.source, self.woof)
