import parser
import metamodule

class Module(metamodule.MetaModule):
    def act(self, message):
        if parser.args(message.content, 'auth', self.conf):
            # Force an authentication check.
            self.irc.who(message.nick)
    
        if parser.args(message.content, 'sit', self.conf):
            # Test authentication status. Will obey if source is authenticated.
            if message.person['master'] == True:
                self.irc.act(message.source, 'sits')
            else:
                self.irc.act(message.source, 'growls')
        
        quote = parser.args(message.content, 'rsend', self.conf)

        if quote and type(quote) != bool and message.person['master'] == True:
            self.irc.irc.send('%s\r\r' % quote)
        elif quote and type(quote) != bool:
            self.irc.act(message.source, 'growls')
