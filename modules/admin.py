import parser
import metamodule

class Module(metamodule.MetaModule):
    def growl(self, target):
        self.irc.act(target, 'growls')

    def act(self, message):
        if parser.args(message.content, 'auth', self.conf):
            # Force an authentication check.
            self.irc.who(message.nick)
    
        if parser.args(message.content, 'sit', self.conf):
            # Test authentication status. Will obey if source is authenticated.
            if message.person['master'] == True:
                self.irc.act(message.source, 'sits')
            else:
                self.growl(message.source)
        
        quote = parser.args(message.content, 'quote', self.conf)
        ctcp = parser.args(message.content, 'ctcp', self.conf)

        
        if (quote and type(quote) != bool) or (ctcp and type(ctcp) != bool):
            if message.person['master'] == True:
                if ctcp:
                    target = ctcp.split(' ')[0]
                    ctcp_type = ctcp.split(' ')[1]
                    try:
                        content = ' '.join(ctcp.split(' ')[2:])
                    except IndexError:
                        content = None
                    
                    self.irc.ctcp(target, ctcp_type, content)

                if quote:
                    self.irc.irc.send('%s\r\r' % quote)

            else:
                self.growl(message.source)
