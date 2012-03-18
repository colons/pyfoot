import parser
import metamodule

class Module(metamodule.MetaModule):
    def act(self, message):
        """ Takes any say command and sends it anywhere. Utterly indiscriminate. """
        post_arg = parser.args(message.content, 'say', self.conf)
        if post_arg:
            if len(post_arg.split()) > 1:
                target = post_arg.split()[0]
                if target.lower() not in conf.get('say_blacklist').split(','):
                    phrase = ' '.join(post_arg.split()[1:])
                    self.irc.send(target, phrase)
