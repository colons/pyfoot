# pyfoot 3.0 configuration file template
##
# This is the configuration file for your pyfoot. Global as well as per network settings go here.
#
# Note: This is a Python 2.7 module, specifically one with one or more dictionaries
# and nothing else. As such, any Python 2.7 code is acceptable here, although it is
# not intended to contain anything other than text. It also must conform to Python's syntax.
# Any configuration options not used will be loaded into pyfoot but ignored;
# therefore it is a good idea to comment out or delete lines not used by your instance.
#
# Follow the examples below and you won't run into any problems.
##
# In the comments, [name] denotes a plugin and 'name' denotes a config setting.
##

GLOBAL = {
        # Identity information for your pyfoot. The only field
        # usually required by a network to be unique is 'nick'.
        'nick': 'pyfoot',
        'hostname': 'pyfoot',
        'servername': 'pyfoot',
        'realname': 'pyfoot',
        'username': 'pyfoot',

        # Default connection profile.
        'network_port': 6667,
        'network_ssl': False,

        # The character set used by your pyfoot. If you don't know what the network's
        # character set is, leave this as UTF-8. If your pyfoot starts seeing lots of garbled
        # or truncated messages, you will need to change this to one of the encodings
        # listed at http://docs.python.org/library/codecs.html#standard-encodings
        'charset': 'utf-8',

        # The character(s) used to invoke commands. Only has effect on plugins that
        # register commands and only if the very first character(s) in the message.
        # This can be specified using Unicode escapes e.g. u'\u300c\u300d' to use
        # U+300C "LEFT CORNER BRACKET" and U+300D "RIGHT CORNER BRACKET" together as a 'comchar'.
        'comchar': u'!',

        # The colour used for prettifying your pyfoot's output. The stock plugins only use
        # this for certain separating characters, although any plugin can use it anywhere.
        # Also used by docs.wsgi to colour the online help pages.
        #
        # Standard colours introduced by mIRC are listed at http://www.mirc.com/colors.html
        # and your pyfoot will automatically strip colours on +c (no colour) channels.
        'pigment': 4,

        # The directory where your pyfoot's local files, such as rantext sources and
        # your default config file, are stored. Must include trailing slash.
        'content-dir': '~/.pyfoot/'

        # The list of plugins you wish to load. Will search both the base
        # plugins directory as well as 'content-dir'plugins for matches.
        'plugins': ['help', 'woof', 'http', 'mal', 'translate', 'party', 'ddg', 'rantext', 'hhg', 'konata', 'ctcp', 'admin', 'weather', 'debug.reencode', 'debug.longtext'],

        # Regular expression used by [woof] as a trigger.
        'woof_trigger': '(?i).*(\\bpy|woo+f|good dog|bad dog|good boy|treat|\\bmeow\\b|\\bbark\\b|\\barf\\b|\\bfetch\\b|\\bmoo+\\b|\\bqua+ck\\b|\\bcluck\\b|\\bwalk\\b|\\bwalkie\\b|\\bwalkies\\b|\\bho+nk\\b|\\bwo+nk\\b|\\bsqua+wk\\b|\\bca+w\\b|\\boink\\b|\\bnya|\\bwan\\b|\\bnyro|\\bgeso|\\bneigh\\b|\\bcollar\\b|\\bawoo+\\b|\\bwan\\b|\\btwee+t\\b).*',
        # The text output by [woof] when the above regex is matched.
        'woof_greeting': 'woof',

        # The default message used when your pyfoot quits a server.
        'quit_message': 'woof',
        # The default message used when a plugin raises an error.
        'error_message': 'rolls over',

        # A list of text files used by [rantext] that contain one message per line.  These must be
        # located in your 'content-dir' (see above), and the command to invoke them is the same as their filename, e.g.:
        # !troll tells [rantext] to return a line from 'content-dir'troll.txt
        'rantext_sources': ['troll'],

        # A random string of bytes used for salting the admin password hashes.
        'admin_salt': '',
        # The nicks and password hashes of your admins. The [admin] plugin will print to
        # the console (not the server) the salted hash of the password used in a failed login.
        'admin_admins': {
            'adminnick': '',
            },

        # An API ID obtained from http://www.bing.com/developers/appids.aspx
        # Used by [translate] and [party] plugins as well as any others that use the Bing API.
        'bing_app_id': '',
        # The URL base of your pyfoot's online help, used in conjunction with docs.wsgi
        # See the documentation for the [help] and [party] plugins for examples of how this is used in context.
        'web_url': 'http://example.org/',

        # Language used by the [party] !party command. !partyvia overrides this per message.
        'party_via': 'ja',
        # The local directory in which party transcriptions are stored. Must include trailing slash.
        'party_dir': '~/.pyfoot/',
        }

# Network profiles (settings specific to a given network) are below.
# While any setting can be located in GLOBAL and can be overridden by
# the equivalent setting in a network profile, the following examples
# are generally server-specific enough to not be included in GLOBAL.
#
# More than one profile may be specified in the configuration, but only
# one profile can be used per pyfoot instance.

# The name of the network profile, used on pyfoot's command line as well
# as by the [help] and [party] plugins as part of their URLs.
networkname = {
        # The domain name or IP address of an IRC network/server.
        'network_address': '127.0.0.1',
        # An example of overriding the GLOBAL settings.
        'network_port': 6697,
        'network_ssl': True,
        # The list of channels to automatically join upon connecting to the server.
        'network_channels': ['#example', '#channels'],
        # The password to provide to NickServ upon successful connection.
        'network_nickserv_pass': '',

        # Ignore list for this network. Although pyfoot must accept all messages,
        # it will not respond in any way to messages from the nicknames listed here.
        'nick_blacklist': ['pyfoot', 'trenchfoot'],

        # A per-plugin blacklist of channels. A given plugin will not
        # respond to any messages in any channels in its blacklist.
        'plugin_blacklist': {
            'konata': ['#pleasenokonata', '#wehatefun'],
            'http': ['#urlspam'],
            },

        # Used by [rss] to determine where to output the headlines of which feeds.
        'rss_feeds': {
            '#nerds': 'http://feeds.arstechnica.com/arstechnica/index/',
            '#nerds': 'https://news.ycombinator.com/rss',
            '#depressme': 'http://news.google.com/news?topic=w&output=rss',
            },
        }
