import sys
import os

class Config(object):
    defaults = {
            'nick': 'pyfoot',
            'hostname': 'pyfoot',
            'servername': 'pyfoot',
            'realname': 'pyfoot',
            'username': 'pyfoot',
            'ctcp_version': 'pyfoot',

            'comchar': '!',

            'content_dir': os.path.expanduser('~/.pyfoot/'),

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

    def __init__(self, network):
        self.conf = self.defaults.copy()

        sys.path.insert(0, self.conf['content_dir'])
        import config

        self.conf.update(getattr(config, 'GLOBAL'))
        self.conf.update(getattr(config, network))
        self.alias = network
        self.conf['alias'] = network

    def get(self, item):
        return self.conf[item]
