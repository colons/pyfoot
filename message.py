import parser

class Message(object):
    def __init__(self, data):
        try:
            self.nick = parser.nick(data)
            self.content = parser.content(data)
            self.source = parser.destination(data)
            self.host = parser.host(data)
        except IndexError:
            # one of these failed, so we can't trust any of them
            self.nick = self.content = self.source = self.host = None
