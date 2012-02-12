import parser

class Module:
    def act(self, message, irc, conf):
        """ Takes any say command and sends it anywhere. Utterly indiscriminate. """
        post_arg = parser.args(message.content, 'say ', conf)
        if post_arg:
            if len(post_arg.split()) > 1:
                target = post_arg.split()[0]
                phrase = ' '.join(post_arg.split()[1:])
                irc.send(target, phrase)
