import urllib

class MetaModule:
    def __init__(self, irc, conf):
        self.irc = irc
        self.conf = conf

    def act(self, message):
        pass

    def translate(self, source, target, phrase):
        """ Translates phrase from source language to target language with Bing's translation API """
        query = urllib.quote(phrase)
        page = urllib.urlopen('http://api.microsofttranslator.com/V2/Ajax.svc/Translate?appId=%s&from=%s&to=%s&text="%s"' % (self.conf.get('bing_app_id'), source, target, query))
        result = page.read()
        if result[4:-1].startswith('ArgumentOutOfRangeException: '):
            raise NameError("that's not a language, silly")
        print result[4:-1]
        return result[4:-1]
