import module

class Module(module.Module):
    def register_commands(self):
        self.regexes = {
                self.conf.get('woof_trigger'): self.woof
                }

    def woof(self, the_message, args):
        """ He's a <a href="http://d.bldm.us/gallery/photos/a3300/120125%20006.jpg">dog</a>; he's excitable. """
        self.irc.send(the_message.source, self.conf.get('woof_greeting'))
