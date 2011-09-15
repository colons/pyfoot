import message
import thread

def content(data):
    return(':'.join(data.split(':')[2:]))

def nick(data):
    return(''.join(data.split(':')[1]).split('!')[0])

def destination(data):
    """ Determines where to send whatever the parser develops """
    destination = ''.join(data.split(':')[:2]).split(' ')[-2]
    if destination.startswith('#'):
        return destination
    else:
        return nick(data)


def args(content, arg, conf):
    prefix = '%s%s' % (conf.get('comchar'), arg)
    if content.startswith(prefix):
        return content[len(prefix):].rstrip("\r\n").strip()
    else:
        return False

def dispatch(data, irc, conf):
    """ Deals with messages, sends modules the information they need. """
    if data == None:
        # For some reason I have yet to work out, some rizon nodes
        # will output data that gets interpreted as None shortly
        # after connect. This bears more investigation, but in the
        # meantime, we'll just ignore it and move on.
        return(None)

    if data.startswith('PING :'):
        print 'PONG!'
        irc.pong(data)
    
    try:
        type = ''.join(data.split(':')[:2]).split(' ')[1]
    except(IndexError):
        type = None
        print 'Unable to determine message type, abandoning parse.'

    # loads the modules from our configfile
    modules = __import__('modules', globals(), locals(), conf.get('modules').split(','))
    
    if type == 'INVITE':
        channel = content(data)
        irc.join(channel)

    if type == 'PRIVMSG':
        the_message = message.Message(data)

        for module in conf.get('modules').split(','):
            thread.start_new_thread(getattr(modules, module).act, (the_message, irc, conf))
