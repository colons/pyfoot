#from BeautifulSoup import BeautifulStoneSoup
import urllib

import module

class Translator(object):
    def __init__(self, bing_app_id):
        self.bing_app_id = bing_app_id

    def translate(self, source, target, phrase):
        """ Translates phrase from source language to target language with Bing's translation API """
        query = urllib.quote(phrase)
        page = urllib.urlopen('http://api.microsofttranslator.com/V2/Ajax.svc/Translate?appId=%s&from=%s&to=%s&text="%s"' % (self.bing_app_id, source, target, query))
        result = page.read()
        if result[4:-1].startswith('ArgumentOutOfRangeException: '):
            raise NameError("that's not a language, silly")
        return result[4:-1]


class Module(module.Module):
    def prepare(self):
        self.translator = Translator(self.conf.get('bing_app_id'))

    def register_commands(self):
        self.commands = [
                ('translate <from> <to> <<phrase>>', self.translate),
                ]

    def translate(self, message, args):
        """ Translates <span class="irc"><span class="repl">phrase</span></span> from <span class="irc"><span class="repl">from</span></span> to <span class="irc"><span class="repl">to</span></span> using the Bing translate API. <span class="irc"><span class="repl">from</span></span> and <span class="irc"><span class="repl">to</span></span> must be any of the language codes <a href="http://msdn.microsoft.com/en-us/library/dd877907.aspx">here</a> and <a href="http://msdn.microsoft.com/en-us/library/dd877886.aspx">here</a>, respectively.
        $<comchar>translate fr en le jambon est mort
        >the ham is dead"""
        print args
        print args['phrase']
        from, to, phrase = (args[key].encode('utf-8') for key in ('from', 'to', 'phrase'))
        print args
        translation = self.translator.translate(args[0], args[1], args[2])
        self.irc.privmsg(message.source, translation)
