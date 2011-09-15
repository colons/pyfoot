import re
import time

def act(message, irc, conf):
    if re.compile(conf.get('woof_trigger')).search(message.content):
        irc.send(message.source, conf.get('woof'))        
