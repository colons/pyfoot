import re
import time
import metamodule

class Module(metamodule.MetaModule):
    """ He's a dog, right? Get it? """
    def __init__(self, irc, conf):
        """ not really necessary, more a proof of concept than anything """
        metamodule.MetaModule.__init__(self, irc, conf)
        self.woof = conf.get('woof')

    def act(self, message, irc, conf):
        if re.compile(conf.get('woof_trigger'), re.IGNORECASE).search(message.content):
            irc.send(message.source, self.woof)
