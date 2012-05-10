import Queue
import threading
import traceback

class Plugin(threading.Thread):
    def __init__(self, irc, conf, prepare=True):
        threading.Thread.__init__(self)

        self.irc = irc
        self.conf = conf
        self.queue = Queue.Queue()
        self.commands = []
        self.regexes = []

        self.error_message = conf.get('error_message')
        
        if prepare:
            try:
                self.prepare()
            except AttributeError:
                pass
    
        try:
            self.register_commands()
        except AttributeError:
            pass

    def run(self):
        try:
            self.postfork()
        except AttributeError:
            pass

        while True:
            function, message, args = self.queue.get()

            try:
                function(message, args)
            except:
                traceback.print_exc()
                self.irc.act(message.source, self.error_message)