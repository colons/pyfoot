import Queue
import threading
import re

class Module(threading.Thread):
    def __init__(self, irc, conf):
        threading.Thread.__init__(self)

        self.irc = irc
        self.conf = conf
        self.queue = Queue.Queue()
        self.commands = False
        self.regexes = False
        
        try:
            self.register_commands()
        except AttributeError:
            pass

        try:
            self.prepare()
        except AttributeError:
            pass
    
    def run(self):
        while True:
            the_message = self.queue.get()

            if self.commands and the_message.content.startswith(self.conf.get('comchar')):
                for command, function in self.commands:
                    args = {}
                    arglist = re.findall('(?<=<).*?(?=>)', command)
                    regex = re.sub('<.*?>', '(.+?)', command+'$')
                    
                    match = re.match(regex, the_message.content[len(self.conf.get('comchar')):])

                    if match:
                        for arg in arglist:
                            args[arg] = match.groups()[arglist.index(arg)].strip()

                        function(the_message, args)
                        break # only one command per module per message
            
            if self.regexes:
                for regex, function in self.regexes:
                    if re.search(regex, the_message.content):
                        function(the_message)
