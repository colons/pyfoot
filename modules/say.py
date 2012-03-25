import parser
import metamodule

class Module(metamodule.MetaModule):
    def act(self, message):
        """ Takes any say command and sends it anywhere. Mostly indiscriminate. """
        post_arg = False
        say = parser.args(message.content, 'say', self.conf)
        act = parser.args(message.content, 'act', self.conf)

        if act:
            post_arg = act
        if say:
            post_arg = say

        if post_arg and type(post_arg) != bool:
            target = post_arg.split()[0]
            if target.lower() not in self.conf.get('say_blacklist').split(','):
                phrase = ' '.join(post_arg.split()[1:])
                
                if say:
                    self.irc.send(target, phrase)
                else:
                    self.irc.act(target, phrase)
