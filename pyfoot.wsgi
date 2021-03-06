#! /usr/bin/env python3

import os
import sys

our_dir = os.path.dirname(os.path.realpath(__file__))

sys.path.append(our_dir)
os.chdir(our_dir)

import bottle
import re
from markdown import markdown

import conf as config_plugin
import plugins
from plugins.help import genderise

# mirc colours
#     0      1      2      3      4      5      6      7      8      9
#     10     11     12     13     14     15
pigments = [
    'aaa', '000', '339', '6a3', 'd66', '960', '93c', 'd73', 'da3', '6a3',
    '8a3', '69d', '36d', 'd69', '666', '999'
]


def remove_control_chars(s):
    """ thanks http://stackoverflow.com/questions/92438/ """
    #control_chars = ''.join(map(unichr, range(0,32) + range(127,160)))
    return re.sub('[\x00-\x1F\x7F-\x9F]', '', s)


def convert_mirc_entities(line):
    odd = True
    while re.search('\x03', line):
        if odd:
            line = re.sub('\x03#', '<span class="pigment">', line, count=1)
        else:
            line = re.sub('\x03', '</span>', line, count=1)
        odd = not odd
    if not odd:
        line += '</span>'

    odd = True
    while re.search('\x02', line):
        if odd:
            line = re.sub('\x02', '<span class="bold">', line, count=1)
        else:
            line = re.sub('\x02', '</span>', line, count=1)
        odd = not odd
    if not odd:
        line += '</span>'

    return line


def parse_paragraph(line, conf):
    line = line.replace('\n', ' ')

    if conf:
        line = line.replace('<comchar>', conf['comchar'])

    if conf.alias != 'GLOBAL':
        line = line.replace('<network>', conf.alias)
    else:
        line = line.replace('<network>', 'network')

    line = line.replace('<pyfoot>', conf['nick'])

    if line.startswith('$'):
        line = convert_mirc_entities(line)
        line = '<p class="input">%s</p>' % line[1:]

    elif line.startswith('>'):
        line = convert_mirc_entities(line)
        line = '<p class="output">%s</p>' % line[1:]
    else:
        line = genderise(line, conf)
        line = markdown(line)

    return line


def examine_function(command, function, conf, regex=False):
    if function.__doc__:
        if not regex:
            command = conf['comchar']+command
            command = command.replace('<<', '<')
            command = command.replace('>>', '>')
            command = remove_control_chars(command)
        else:
            # Ensures the regex comes through literally and spaces don't break
            # lines for style reasons.
            command = re.findall('(?<=[\'"]).*(?=[\'"])', repr(command))[0]
            command = command.replace(' ', '\u00A0')
            command = re.sub('(.)(?=[^\\Z])', '\\1\u200B', command)

        docstring = function.__doc__
        doc_lines = docstring.split('\n\n')

        explanation = []
        for line in [l.strip() for l in doc_lines if len(l.strip()) > 0]:
            explanation.append(parse_paragraph(line, conf))

        docstring = '\n'.join(explanation)

        if regex and len(command) > 80:
            command = command[:80]+'...'

        return {
            'command': command,
            'docstring': docstring,
        }


class App(bottle.Bottle):
    def __init__(self):
        bottle.Bottle.__init__(self)

        self.global_conf = config_plugin.Config('GLOBAL')

        bottle.TEMPLATE_PATH.append('./plugins/tpl')
        bottle.TEMPLATE_PATH.append(
            '%s/plugins/tpl' % self.global_conf['content_dir'])

        self.networks = {
            name: self.inspect_network(config_plugin.Config(name))
            for name in self.global_conf['networks']+['GLOBAL']}

    def inspect_network(self, conf):
        tpl_dir = '%s/plugins/tpl' % conf['content_dir']
        if tpl_dir not in bottle.TEMPLATE_PATH:
            bottle.TEMPLATE_PATH.append(tpl_dir)

        plugin_list = []

        plugins.__path__.insert(0, '%s/plugins/' % conf['content_dir'])

        for plugin_name in conf['plugins']:
            __import__('plugins.'+plugin_name)
            plugin = sys.modules['plugins.%s' % plugin_name]

            try:
                plugin.defaults
            except AttributeError:
                pass
            else:
                for key in plugin.defaults:
                    if key not in conf:
                        conf[key] = plugin.defaults[key]

            setattr(plugin.Plugin, 'name', plugin_name)
            plugin_instance = plugin.Plugin(
                None, conf, prepare=False, bottle=self)

            plugin_list.append(plugin_instance)

        plugin_dicts = []

        for plugin in plugin_list:
            functions = []

            if plugin.commands:
                for command, function in plugin.commands:
                    entry = examine_function(command, function, conf)
                    if entry:
                        functions.append(entry)

            if plugin.regexes:
                for command, function in plugin.regexes:
                    entry = examine_function(
                        command, function, conf, regex=True)
                    if entry:
                        functions.append(entry)

            if plugin.urls:
                for path, function in plugin.urls:
                    self.route(path, callback=function)

            plugin_dict = {
                'name': plugin.name,
                'functions': functions,
            }

            try:
                plugin_dict['docstring'] = '\n'.join([
                    parse_paragraph(l.strip(), conf) for l in
                    plugin.__doc__.split('\n\n') if len(l.strip()) > 0])
            except AttributeError:
                plugin_dict['docstring'] = None

            try:
                plugin_dict['blacklist'] = [
                    c for c in conf['plugin_blacklist']
                    if plugin.name in conf['plugin_blacklist'][c]]
            except KeyError:
                plugin_dict['blacklist'] = False

            plugin_dicts.append(plugin_dict)

        return plugin_dicts

app = App()


@app.route('/')
def redir_to_help():
    bottle.redirect("/help/")


@app.route('/static/<filename>')
def server_static(filename):
    return bottle.static_file(filename, root=os.getcwd()+'/static')


@app.route('/<network>.css')
def css(network):
    bottle.response.set_header('Content-type', 'text/css')
    try:
        conf = config_plugin.Config(network)
    except AttributeError:
        raise bottle.HTTPError(code=404)

    pigment = '#%s' % pigments[int(str(conf['pigment']).split(',')[0])]

    return bottle.template('tpl/css', pigment=pigment)

if __name__ == '__main__':
    bottle.run(app=app, host='0.0.0.0', port=8080)
