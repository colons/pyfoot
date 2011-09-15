import ConfigParser

class NetworkConf(object):
    """ A configuration reader """
    def __init__(self, network, configfile):
        """ read the configfile parts necessary for whatever network we're on and set self.network up as a thing """
        self.config = ConfigParser.ConfigParser()
        self.config.read(configfile)
        self.network = network

    def get(self, item):
        """ Retrieves an item from the config for the network we decided we want to use """
        return self.config.get(self.network, item)
