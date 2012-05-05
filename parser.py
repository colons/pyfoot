import message
import thread
import chardet

def content(data):
    """ Return message content """
    line = ':'.join(data.split(':')[2:])
    return unicode(line, chardet.detect(line)['encoding'])

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


def dispatch(data, irc, modules, conf):
    """ Deals with messages and sends modules the information they need. """
    if data == None:
        print ' :: no data'
        return None
    
    if data == '':
        print ' :: empty response, assuming disconnection\a' # alert
        irc.close()

    for line in data.split('\r\n'):

        if line.startswith('PING :'):
            irc.pong(line)
        
        try:
            type = ''.join(line.split(':')[:2]).split(' ')[1]
        except(IndexError):
            type = None
        else:
            the_message = message.Message(line)
            
            if the_message.host:
                # who is this from? do we already know who they are?
                try:
                    the_message.person = irc.people[the_message.host]
                except KeyError:
                    irc.people[the_message.host] = {'nick': the_message.nick, 'master': False}
                    the_message.person = irc.people[the_message.host]
                
                if the_message.person['nick'] != the_message.nick:
                    print ' :: %s has become %s since we last saw them' % (the_message.person['nick'], the_message.nick)
                    the_message.person['nick'] = the_message.nick

        if type == '324':
            # this is a list of channel modes
            splitline = line.split(' ')
            name = splitline[3]
            modelist = splitline[4]

            try:
                irc.channels[name]['modes'] = modelist.lstrip('+')
            except KeyError:
                irc.channels[name] = {'modes': modelist.lstrip('+')}

        if type == '352':
            # this is a WHO response
            splitline = line.split(' ')
            name = splitline[4]
            modelist = splitline[8]
            host = splitline[4]+'@'+splitline[5]

            irc.people[host]['modes'] = modelist

            if 'r' in modelist and name in conf.get('masters').split(','):
                irc.people[host]['master'] = True

        if type == 'MODE':
            name = line.split(' ')[2]
            irc.getmode(name)

        if type == 'KICK':
            name = line.split(' ')[2]

            try:
                del irc.channels[name]
            except KeyError:
                print ' :: was just kicked from %s, a channel we were not aware of being in'
        
        if type == 'INVITE':
            channel = content(line)
            irc.join(channel)

        if type == 'NOTICE':
            if the_message.nick == 'NickServ':
                if irc.initial:
                    irc.send('nickserv', 'identify %s' % conf.get('nickserv_pass'))

                for channel in conf.get('channels').split(','):
                    irc.join(channel)
                
                irc.initial = False

        if type == 'NICK':
            try:
                irc.people[the_message.host]
            except KeyError:
                irc.people[the_message.host] = {}

            irc.people[the_message.host]['nick'] = the_message.content

        if type == 'PRIVMSG':
            if the_message.nick.lower() not in [n.lower() for n in conf.get('blacklist').split(',')]:
                for module in modules:
                    if '%s %s' % (the_message.source, module.name) not in conf.get('exclude').split(','):
                        if conf.get('debug') == '1':
                            module.act(the_message)
                        else:
                            thread.start_new_thread(module.act, (the_message,))
