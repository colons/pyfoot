def content(data, charset):
    """ Return message content """
    if charset == 'utf-8':
        return ':'.join(data.split(':')[2:])
    else:
        return ':'.join(data.split(':')[2:]).decode(charset).encode('utf-8')

def nick(data):
    """ Return message nick """
    return ''.join(data.split(':')[1]).split('!')[0]

def host(data):
    """ Return message nick """
    return ''.join(data.split(':')[1]).split('!')[1].split(' ')[0]

def destination(data):
    """ Determines where to send whatever the parser develops """
    destination = ''.join(data.split(':')[:2]).split(' ')[-2]
    if destination.startswith('#'):
        return destination
    else:
        return nick(data)

def args(content, args, conf):
    """ Determines what arguments a message contains """
    if type(args) == list:
        prefixes = ['%s%s' % (conf.get('comchar'), arg) for arg in args]
    else:
        prefixes = ['%s%s' % (conf.get('comchar'), args)]

    if content.split(' ')[0].strip() in prefixes:
        post_args = ' '.join(content.split(' ')[1:]).rstrip("\r\n").strip()
        if len(post_args) != 0:
            return post_args
        else:
            return True
    else:
        return False


class Message(object):
    def __init__(self, data, charset):
        try:
            self.type = ''.join(data.split(':')[:2]).split(' ')[1]
        except IndexError:
            self.type = None

        try:
            self.nick = nick(data)
            self.content = content(data, charset)
            self.source = destination(data)
            self.host = host(data)
        except IndexError:
            # one of these failed, so we can't trust any of them
            self.nick = self.content = self.source = self.host = None

