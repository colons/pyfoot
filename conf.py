import sys
from os.path import expanduser
from re import match


class Config(object):
    defaults = {
        'nick': 'pyfoot',
        'hostname': 'pyfoot',
        'servername': 'pyfoot',
        'realname': 'pyfoot',
        'username': 'pyfoot',
        'ctcp_version': 'pyfoot',

        'gender': 'neutral',

        'comchar': '!',

        'content_dir': expanduser('~/.pyfoot/'),

        'web_url': 'http://woof.bldm.us/',

        'quit_message': 'woof',
        'error_message': 'rolls over',
        'pigment': 4,

        'network_address': 'localhost',
        'network_port': 6667,
        'network_ssl': False,
        'network_channels': [],

        'charset': 'utf-8',

        'plugins': ['help', 'admin'],

        'plugin_blacklist': {},

        'nick_blacklist': [],

        'single_instance': False,
        'restart_from_webapp': True,

        'url_shortener': 'http://waa.ai/api.php?url=%s',
    }

    def __init__(self, network, conffile=None):
        self.conf = self.defaults.copy()

        if conffile:
            try:
                confpath, confmod = match('(.*/)(.*)', conffile).groups()
            except AttributeError:
                confmod = conffile
            else:
                sys.path.insert(0, confpath)
            config = __import__(confmod.split('.')[0])
        else:
            sys.path.insert(0, self.conf['content_dir'])
            import config

        self.conf.update(getattr(config, 'GLOBAL'))
        self.conf.update(getattr(config, network))
        self.alias = network
        self.conf['alias'] = network

        self.conf['pnoun_neutral'] = {
            'nom': 'xe',
            'obl': 'xem',
            'pos_det': 'xyr',
            'pos_pro': 'xyrs',
            'reflex': 'xemself',
        }

        if self.conf['gender'] == 'male':
            self.conf['pnoun'] = {
                'nom': 'he',
                'obl': 'him',
                'pos_det': 'his',
                'pos_pro': 'his',
                'reflex': 'himself',
            }

        elif self.conf['gender'] == 'female':
            self.conf['pnoun'] = {
                'nom': 'she',
                'obl': 'her',
                'pos_det': 'her',
                'pos_pro': 'hers',
                'reflex': 'herself',
            }

        else:
            self.conf['pnoun'] = self.conf['pnoun_neutral']

        # Make sure to expand the user's 'content-dir'.
        is_in_home = self.conf['content_dir'].find('~')
        if is_in_home != -1:
            self.conf['content_dir'] = expanduser(self.conf['content_dir'])

    def get(self, key):
        return self.conf[key]
