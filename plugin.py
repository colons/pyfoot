import queue
import threading
import traceback
from urllib import request
from urllib.parse import quote


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

        self.error_message = conf['error_message']

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

    def send_struc(self, destination, structure):
        """
        Send a list of strings or list of lists of strings to a given
        destination. It'll be pretty, I promise.
        """

        elements = []

        for item in structure:
            if type(item) == str:
                elements.append(item)
            else:
                elements.append('\x03# :\x03 '.join(item))

        string = '\x03# |\x03 '.join(elements)
        self.irc.privmsg(destination, string)

    def shorten_url(self, url):
        try:
            response = request.urlopen(
                self.conf.get('url_shortener') % quote(url))
        except:
            return url
        else:
            return response.read().decode('utf-8')
