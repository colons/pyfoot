import message
import thread


def parse_modelist(modelist):
    modelist = modelist.lstrip('+')
    return modelist

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


def dispatch(data, irc, modules, conf):
    """ Deals with messages, sends modules the information they need. """
    if data == None:
        print ' :: no data'
        return None
    
    if data == '':
        print ' :: empty response, assuming disconnection\a' # alert
        irc.close()

    for line in data.split('\n'):
        if line.startswith('PING :'):
            print 'PONG!'
            irc.pong(line)
        
        try:
            type = ''.join(line.split(':')[:2]).split(' ')[1]
        except(IndexError):
            type = None
        
        try:
            int(type)
        except(ValueError, TypeError):
            pass
        else:
            # this is a status message, if it's modes we need to know about it
            splitline = line.split(' ')
            try:
                channel_name = splitline[3]
            except IndexError:
                pass
            else:
                if channel_name.startswith('#'):
                    modelist = splitline[4]

                    if modelist.startswith('+'):
                        irc.channels[channel_name] = parse_modelist(modelist)
                        print irc.channels

        if type == 'MODE':
            channel_name = line.split(' ')[2]
            irc.join(channel_name)

        if type == 'KICK':
            channel_name = line.split(' ')[2]
            del irc.channels[channel_name]
            print irc.channels
        
        if type == 'INVITE':
            channel = content(line)
            irc.join(channel)

        if type == 'NOTICE':
            the_message = message.Message(line)

            if the_message.nick == 'NickServ':
                # this is a horrible hack - we attempt channel joins when nickserv talks to us
                # which should only happen shortly after joining
                # this means we can get into +r channels
                for channel in conf.get('channels').split(','):
                    irc.join(channel)

        if type == 'PRIVMSG':
            the_message = message.Message(line)

            if the_message.nick not in conf.get('blacklist').split(','):
                for module in modules:
                    if '%s %s' % (the_message.source, module.name) not in conf.get('exclude').split(','):
                        if conf.get('debug') == '1':
                            module.act(the_message)
                        else:
                            thread.start_new_thread(module.act, (the_message,))
