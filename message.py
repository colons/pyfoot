import parser

class Message(object):
    def __init__(self, data):
        self.nick = parser.nick(data)
        self.content = parser.content(data)
        self.source = parser.destination(data)

