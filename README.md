pyfoot
======

An extensible IRC robot with automatically generated user documentation.

Features
--------

Why use pyfoot, you ask? Well, *let me show you*.

### Documentation all over the place

Documentation is important, especially if you’re looking to deploy your robot
in a high-traffic channel with trigger-happy operators. pyfoot attempts to make
documentation as complete and as hassle-free as possible for all involved.

#### Out-of-channel

[This page](http://woof.bldm.us/help/rizon/) is the documentation for my pyfoot
instance that runs on Rizon. The page is generated in a
[Bottle](http://bottlepy.org/) automatically, based on that network’s specific
configuration and docstrings in the plugins themselves. All documentation is
kept in context and the help page will always reflect the current state of your
pyfoot instance.

#### In-channel

When queried with a !help command (the command delimiter can be anything, I’m
using ! here as an example), pyfoot will respond with a selection of
appropriate commands that could match, along with links to the relevant online
documentation.
    
```irc
< luser> !help !ddg
<&pyfoot> ddg | !ddg <query> | http://woof.bldm.us/help/rizon/#ddg
< luser> !help p
<&pyfoot> admin | !part <channel> <reason> : !part <channel> | http://woof.bldm.us/help/nnchan/#admin
<&pyfoot> party | !party <phrase> | http://woof.bldm.us/help/nnchan/#party
```

### Easy extensibility

The environment that pyfoot’s plugins live in is simple, consistent and flexible. For
some examples, see the Plugin Development tutorial below.

### And more…

* Automatic handling of abbreviated commands to the point of ambiguity
* Automatic mIRC format stripping in +c channels
* Pretty, colour-configurable output
* [Very liberal](http://sam.zoy.org/wtfpl/) distribution terms
* A [bunch] [plugins] of
  [pointless](https://github.com/colons/pyfoot-plugins/blob/master/konata.py)
  [plugins](https://github.com/colons/pyfoot-plugins/blob/master/woof.py)

Setup and Use
-------------

You’ll need a folder called `~/.pyfoot` and, within it, a `config.py` (see
`config.example.py` in this repo for an example).  You will probably also want
to put any custom plugins into `~/.pyfoot/plugins/`. I just run with
[pyfoot-plugins] [plugins] cloned to that directory, but it’s up to you. For
specifics on configuring individual plugins, see the plugins themselves.

Plugin Development
------------------

There’s no tutorial yet. For the moment, have a look at some
[plugins] [plugins] and try to work things out.
[konata](https://github.com/colons/pyfoot-plugins/blob/master/konata.py) is the
simplest one there.


[plugins]: https://github.com/colons/pyfoot-plugins
