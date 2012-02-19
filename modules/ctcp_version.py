import metamodule

class Module(metamodule.MetaModule):
    def act(self, message):
        if message.content.startswith('VERSION') and not message.source.startswith('#'):
            self.irc.send(message.source, self.conf.get('ctcp_version'))
