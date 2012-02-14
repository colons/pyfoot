import parser
import metamodule

class Module(metamodule.MetaModule):
    def act(self, message, irc, conf):
        """ Sends the konata message. No, it is not configurable. Why would you want it to be? """
        konata = parser.args(message.content, 'konata ', conf)
        if konata != False:
            irc.send(message.source, 'I like %s because she is a otaku like me, except she has friends. Oh god I wish I had friends too ;_;' % konata)
            irc.send(message.source, '%s also likes videogames and she is kawaii. And there are lesbians in the show and that\'s good because I like lesbians and I will never have a girlfriend. Why am I such a loser?!' % konata)
            irc.send(message.source, '%s is like my dreamgirl she has a :3 face I love that. She is also nice why aren\'t real girls nice!? I got dumped a lot of times but I love %s and she wouldn\'t dump me because she\'s so nice and cool.' % (konata, konata))
            irc.send(message.source, 'We would play videogames all day and watch Naruto and other cool animes on TV, and I would have sex with her because sex is so good. I wish I could have sex with a girl')
