def act(message, irc, conf):
    if message.content.startswith('VERSION') and not message.source.startswith('#'):
        irc.send(message.source, conf.get('ctcp_version'))
