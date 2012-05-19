def content(data, charset='ascii'):
    """ Return message content in both UTF-8-encoded and raw forms """
    decruft = lambda line: ':'.join(line.split(':')[2:])
    raw = decruft(data)

    try:
        content = data.decode(charset)
    except UnicodeDecodeError:
            print '\n !! Some characters could not be reproduced in the above input using \'charset\': \'%s\'' % charset
            if len(data) == 510:
                print ' !! The input length was at maximum; the message may have been truncated.'
            content = data.decode(charset, 'ignore')

    content = decruft(content).encode('utf-8')
    return (content, raw)

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
            self.content, self.content_raw = content(data, charset)
            self.source = destination(data)
            self.host = host(data)
        except IndexError:
            # one of these failed, so we can't trust any of them
            self.nick = self.content_raw = self.content = self.source = self.host = None

