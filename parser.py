import message
import thread

def content(data):
    """ Return message content """
    return(':'.join(data.split(':')[2:]))

def nick(data):
    """ Return message nick """
    return(''.join(data.split(':')[1]).split('!')[0])

def destination(data):
    """ Determines where to send whatever the parser develops """
    destination = ''.join(data.split(':')[:2]).split(' ')[-2]
    if destination.startswith('#'):
        return destination
    else:
        return nick(data)


def args(content, arg, conf):
    """ Determines what arguments a message contains """
    prefix = '%s%s' % (conf.get('comchar'), arg)
    if content.startswith(prefix):
        return content[len(prefix):].rstrip("\r\n").strip()
    else:
        return False

def dispatch(data, irc, modules, conf):
    """ Deals with messages, sends modules the information they need. """
    if data == None:
        return None

    for line in data.split('\n'):
        if line.startswith('PING :'):
            print 'PONG!'
            irc.pong(line)
        
        try:
            type = ''.join(line.split(':')[:2]).split(' ')[1]
        except(IndexError):
            type = None

        # loads the modules from our configfile
        
        if type == 'INVITE':
            channel = content(line)
            irc.join(channel)

        if type == 'PRIVMSG':
            the_message = message.Message(line)

            for module in modules:
                module.act(the_message, irc, conf)
                # thread.start_new_thread(module.act, (the_message, irc, conf))
