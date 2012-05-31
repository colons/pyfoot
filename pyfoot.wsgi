#!/usr/bin/env python3.2

import os, sys

dir = os.path.dirname(__file__)

sys.path.append(dir)
os.chdir(dir)

import bottle
from random import choice
import re

import conf as config_plugin
import plugins


# mirc       0      1      2      3      4      5      6      7      8      9      10     11     12     13     14     15
pigments = ['aaa', '000', '339', '6a3', 'd66', '960', '93c', 'd73', 'da3', '6a3', '8a3', '69d', '36d', 'd69', '666', '999']

def remove_control_chars(s):
    """ thanks http://stackoverflow.com/questions/92438/stripping-non-printable-characters-from-a-string-in-python """
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

def genderise(line, conf):
    for pnoun_type in conf.conf['pnoun_neutral']:
        match_pnoun = conf.conf['pnoun_neutral'][pnoun_type]
        repl_pnoun = conf.conf['pnoun'][pnoun_type]
        
        pn_regex = r'(?i)\b(%s)\b' % match_pnoun

        for match in re.findall(pn_regex, line):
            if match[0].isupper():
                repl = repl_pnoun.capitalize()
            else:
                repl = repl_pnoun.lower()

            line = re.sub(pn_regex, repl, line, count=1)

    return line

def parse_paragraph(line, conf):
    if conf:
        line = line.replace('<comchar>', conf.conf['comchar'])

    if conf.alias != 'GLOBAL':
        line = line.replace('<network>', conf.alias)
    else:
        line = line.replace('<network>', 'network')

    line = line.replace('<pyfoot>', conf.conf['nick'])

    if line.startswith('$'):
        line = convert_mirc_entities(line)
        line = '<p class="input">%s</p>' % line[1:]

    elif line.startswith('>'):
        line = convert_mirc_entities(line)
        line = '<p class="output">%s</p>' % line[1:]
    else:
        line = '<p>%s</p>' % line
        line = genderise(line, conf)

    return line


def examine_function(command, function, conf, regex=False):
    if function.__doc__:
        if not regex:
            command = conf.conf['comchar']+command
            command = command.replace('<<', '<')
            command = command.replace('>>', '>')
            command = remove_control_chars(command)
        else:
            # Ensures the regex comes through literally and spaces don't break lines for style reasons.
            command = re.findall('(?<=[\'"]).*(?=[\'"])', repr(command))[0]
            command = command.replace(' ', '\u00A0')
            command = re.sub('(.)(?=[^\\Z])', '\\1\u200B', command)


        docstring = function.__doc__
        doc_lines = docstring.split('\n')

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


def get_entries(network, app):
    if network:
        try:
            conf = config_plugin.Config(network)
        except AttributeError:
            raise bottle.HTTPError(code=404)
    else:
        conf = config_plugin.Config('GLOBAL')

    plugin_list = []

    plugins.__path__.insert(0, '%s/plugins/' % conf.conf['content_dir'])

    for plugin_name in conf.conf['plugins']:
        __import__('plugins.'+plugin_name)
        plugin = sys.modules['plugins.%s' % plugin_name]

        try:
            plugin.defaults
        except AttributeError:
            pass
        else:
            for key in plugin.defaults:
                if key not in conf.conf:
                    conf.conf[key] = plugin.defaults[key]

        setattr(plugin.Plugin, 'name', plugin_name)
        plugin_instance = plugin.Plugin(None, conf, prepare=False, bottle=app)

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
                entry = examine_function(command, function, conf, regex=True)
                if entry:
                    functions.append(entry)


        plugin_dict = {
            'name': plugin.name,
            'functions': functions,
            }

        try:
            plugin_dict['docstring'] = '\n'.join([parse_paragraph(l.strip(), conf) for l in plugin.__doc__.split('\n') if len(l.strip()) > 0])
        except AttributeError:
            plugin_dict['docstring'] = None

        try:
            plugin_dict['blacklist'] = [c for c in conf.conf['plugin_blacklist'] if plugin.name in conf.conf['plugin_blacklist'][c]]
        except KeyError:
            plugin_dict['blacklist'] = False

        plugin_dicts.append(plugin_dict)

    return (plugin_dicts, conf)

app = bottle.default_app()

@app.route('/')
def redir_to_help():
    bottle.redirect("/help/")

@app.route('/<network>.css')
def css(network):
    bottle.response.set_header('Content-type', 'text/css')
    try:
        conf = config_plugin.Config(network)
    except AttributeError:
        raise bottle.HTTPError(code=404)

    pigment = '#%s' % pigments[int(str(conf.conf['pigment']).split(',')[0])]

    return bottle.template('tpl/css', pigment=pigment)

@app.route('/static/<filename>')
def server_static(filename):
    return bottle.static_file(filename, root='/home/nivi/pyfoot/static/') # WHEN PYFOOT IS APP-ISED, THIS NEEDS TO BE DERIVED FROM CONFIG OR SOME SHIT

@app.route('/help/')
def defaults():
    plugin_dicts, conf = get_entries(None, app)
    return bottle.template('tpl/docs', plugins=plugin_dicts, conf=conf.conf, per_network=False)

@app.route('/help/<network>/')
def per_network(network):
    plugin_dicts, conf = get_entries(network, app)
    return bottle.template('tpl/docs', plugins=plugin_dicts, conf=conf.conf, per_network=True)

@app.route('/party/<network>/')
def party_index(network):
    try:
        conf = config_plugin.Config(network)
    except AttributeError:
        raise bottle.HTTPError(code=404)

    parties = []
    party_path = os.path.expanduser(conf.conf['party_dir'])+network

    try:
        party_files = os.listdir(party_path)
    except IOError:
        raise bottle.HTTPError(code=404)

    for party_filename in party_files:
        party_file = open(party_path+'/'+party_filename)
        party = party_file.readlines()

        if party[0].startswith('source: '):
            party = party[1:]

        party_file.close()
        party_dict = {
                'nick': '-'.join(party_filename.split('-')[:-2]),
                'date': party_filename.split('-')[-2],
                'time': party_filename.split('-')[-1][:-4],
                'initial': party[0],
                'final': party[-1],
                'length': len(party),
                'url': party_filename[:-4]+'/',
                }

        parties.append(party_dict)

    parties.sort(key=lambda p:int(p['date']+p['time']), reverse=True)
    return bottle.template('tpl/party_index', parties=parties, network=network)
    party.close()


@app.route('/party/<network>/<filename>/')
def party(network, filename):
    conf = config_plugin.Config(network)
    try:
        party_file = open(os.path.expanduser(conf.conf['party_dir'])+network+'/'+filename+'.txt')
    except IOError:
        raise bottle.HTTPError(code=404)
    else:
        party_lines = party_file.readlines()
        party_file.close()

        if party_lines[0].startswith('source: '):
            party_lines = party_lines[1:]


    party = {
            'lines': party_lines,
            'nick': '-'.join(filename.split('-')[:-2]),
            'date': filename.split('-')[-2],
            'time': filename.split('-')[-1],
            }

    return bottle.template('tpl/party', party=party, network=network)

if __name__ == '__main__':
    bottle.run(app=app, host='0.0.0.0', port=8080)
