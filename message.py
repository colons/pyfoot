def content(data, raw):
    """ Return message content in both Unicode and raw forms """
    return (decruft(data), decruft(raw))


def nick(data):
    """ Return message nick """
    return ''.join(data.split(':')[1]).split('!')[0]


def host(data):
    """ Return message nick """
    return ''.join(data.split(':')[1]).split('!')[1].split(' ')[0]


def destination(data):
    """ Determines where to send whatever the parser develops """
    destination = ''.join(data.split(':')[:2]).split(' ')[2]
    if destination.startswith('#'):
        return destination
    else:
        return nick(data)


def decruft(line):
    if isinstance(line, bytes):
        return b':'.join(line.split(b':')[2:])
    else:
        return ':'.join(line.split(':')[2:])


def args(content, args, conf):
    """ Determines what arguments a message contains """
    if type(args) == list:
        prefixes = ['%s%s' % (conf['comchar'], arg) for arg in args]
    else:
        prefixes = ['%s%s' % (conf['comchar'], args)]

    if content.split(' ')[0].strip() in prefixes:
        post_args = ' '.join(content.split(' ')[1:]).rstrip("\r\n").strip()
        if len(post_args) != 0:
            return post_args
        else:
            return True
    else:
        return False


class Message(object):
    def __init__(self, data, data_raw):
        try:
            self.type = ''.join(data.split(':')[:2]).split(' ')[1]
        except IndexError:
            self.type = None

        try:
            self.nick = nick(data)
            self.content, self.content_raw = content(data, data_raw)
            self.source = destination(data)
            self.host = host(data)
        except IndexError:
            # one of these failed, so we can't trust any of them
            self.nick = self.content_raw = self.content = self.source = None
            self.host = None
