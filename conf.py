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

            'plugin_blacklist': {
                },
            'nick_blacklist': [],
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
