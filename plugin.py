import queue
import threading
import traceback

class Plugin(threading.Thread):
    def __init__(self, irc, conf, prepare=True, bottle=None):
        threading.Thread.__init__(self)

        self.irc = irc
        self.conf = conf
        self.bottle = bottle

        self.queue = queue.Queue()
        self.commands = []
        self.regexes = []
        self.urls = []

        self.error_message = conf.conf['error_message']

        if self.bottle:
            try:
                self.register_urls()
            except AttributeError:
                pass

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
