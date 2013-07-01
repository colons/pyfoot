from os import path, makedirs
import queue
import traceback
from threading import Thread
from urllib import request
from urllib.parse import quote
import shelve


class Plugin(Thread):
    queue = queue.Queue()
    commands = []
    regexes = []
    urls = []
    shelf_required = False

    def __init__(self, irc, conf, prepare=True, bottle=None):
        Thread.__init__(self)

        self.irc = irc
        self.conf = conf
        self.bottle = bottle
        self.name = self.__module__.rsplit('.', 1)[-1]

        if self.shelf_required:
            self._open_shelf()

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

    def _open_shelf(self):
        content_path = path.expanduser(self.conf['content_dir'])
        shelf_dir = path.join(content_path, 'shelf', self.conf.alias)

        if not path.exists(shelf_dir):
            makedirs(shelf_dir)

        shelf_path = path.join(shelf_dir, self.name)

        self.shelf = shelve.open(shelf_path, writeback=True)

    def run(self):
        try:
            self.postfork()
        except AttributeError:
            pass

        while True:
            item = self.queue.get()

            if item == 'panic':
                self.panic()
            else:
                function, message, args = item
                try:
                    function(message, args)
                except:
                    traceback.print_exc()
                    self.irc.act(message.source, self.conf['error_message'])

    def panic(self):
        if self.shelf_required:
            self.shelf.close()

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
        safe_string = string.replace('\r', '').replace('\n', ' ')

        self.irc.privmsg(destination, safe_string)

    def shorten_url(self, url):
        try:
            response = request.urlopen(
                self.conf['url_shortener'] % quote(url))
        except:
            return url
        else:
            return response.read().decode('utf-8')
