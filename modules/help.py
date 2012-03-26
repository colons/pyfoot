import parser
import metamodule

class Module(metamodule.MetaModule):
    def act(self, message):
        """ HALP """
        help = parser.args(message.content, 'help', self.conf)
        if help:
            self.irc.send(message.source, '\x02features\x02 \x034:\x03 http://woof.bldm.us/help/ \x034|\x03 \x02code\x02\x034 :\x03 https://bitbucket.org/colons/pyfoot/ \x034|\x03 \x02bug?\x02\x034 :\x03 https://bitbucket.org/colons/pyfoot/issues/new')
