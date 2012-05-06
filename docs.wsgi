#!/usr/bin/env python2

import os, sys

dir = os.path.dirname(__file__)

sys.path.append(dir)
os.chdir(dir)

import bottle
from random import choice
import re

import conf as config_module

def convert_mirc_entities(line):
    odd = True
    while re.search('\x03', line):
        if odd:
            line = re.sub('\x03\d?\d?', '<span class="red">', line, count=1)
        else:
            line = re.sub('\x03', '</span>', line, count=1)
        odd = not odd

    odd = True
    while re.search('\x02', line):
        if odd:
            line = re.sub('\x02', '<span class="bold">', line, count=1)
        else:
            line = re.sub('\x02', '</span>', line, count=1)
        odd = not odd

    return line


def parse_paragraph(line, conf):
    if conf: 
        line = line.replace('<comchar>', conf.get('comchar'))
        
    if conf.alias != 'GLOBAL':
        line = line.replace('<network>', conf.alias)
    else:
        line = line.replace('<network>', 'network')

    line = line.replace('<pyfoot>', conf.get('nick'))


    if line.startswith('$'):
        line = convert_mirc_entities(line)
        line = '<p class="input">%s</p>' % line[1:]

    elif line.startswith('>'):
        line = convert_mirc_entities(line)
        line = '<p class="output">%s</p>' % line[1:]
    else:
        line = '<p>%s</p>' % line

    return line


def examine_function(command, function, conf, regex=False):
    if function.__doc__:
        if not regex:
            command = conf.get('comchar')+command

        docstring = function.__doc__
        doc_lines = docstring.split('\n')

        explanation = []
        for line in [l.strip() for l in doc_lines if len(l.strip()) > 0]:
            explanation.append(parse_paragraph(line, conf))

        docstring = '\n'.join(explanation)

        if regex and len(command) > 40:
            command = command[:40]+'...'
        
        return {
            'command': command,
            'docstring': docstring,
            }


def get_entries(network):
    if network:
        try:
            conf = config_module.Config(network)
        except AttributeError:
            raise bottle.HTTPError(code=404)
    else:
        conf = config_module.Config('GLOBAL')

    modules = []

    for modulename in conf.get('modules'):
        __import__('modules.'+modulename)
        module = sys.modules['modules.'+modulename]
        setattr(module.Module, 'name', modulename)
        modules.append(module.Module(None, conf))
        modules[-1].setDaemon(False)
    
    module_dicts = []

    for module in modules:
        functions = []

        if module.commands:
            for command, function in module.commands:
                entry = examine_function(command, function, conf)
                if entry:
                    functions.append(entry)

        if module.regexes:
            for command, function in module.regexes:
                entry = examine_function(command, function, conf, regex=True)
                if entry:
                    functions.append(entry)

        
        module_dict = {
            'name': module.name,
            'functions': functions,
            }

        try:
            module_dict['docstring'] = '\n'.join([parse_paragraph(l.strip(), conf) for l in module.__doc__.split('\n') if len(l.strip()) > 0])
        except AttributeError:
            module_dict['docstring'] = None

        try:
            module_dict['blacklist'] = conf.get('module_blacklist')[module.name]
        except KeyError:
            module_dict['blacklist'] = False

        module_dicts.append(module_dict)
        
    return (module_dicts, conf)

@bottle.route('/')
def redir_to_help():
    bottle.redirect("/help")

@bottle.route('/help')
@bottle.route('/help/')
def defaults():
    module_dicts, conf = get_entries(None)
    return bottle.template('tpl/docs', modules=module_dicts, conf=conf.conf, per_network=False)

@bottle.route('/help/<network>/')
def per_network(network):
    module_dicts, conf = get_entries(network)
    return bottle.template('tpl/docs', modules=module_dicts, conf=conf.conf, per_network=True)

@bottle.route('/party/<network>/')
def party_index(network):
    try:
        conf = config_module.Config(network)
    except AttributeError:
        raise bottle.HTTPError(code=404)

    parties = []
    party_path = os.path.expanduser(conf.get('party_dir'))+network

    try:
        party_files = os.listdir(party_path)
    except IOError:
        raise bottle.HTTPError(code=404)

    for party_filename in party_files:
        party_file = open(party_path+'/'+party_filename)
        party = party_file.readlines()
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


@bottle.route('/party/<network>/<filename>/')
def party(network, filename):
    conf = config_module.Config(network)
    try:
        party_file = open(os.path.expanduser(conf.get('party_dir'))+network+'/'+filename+'.txt')
    except IOError:
        raise bottle.HTTPError(code=404)
    else:
        party_lines = party_file.readlines()
        party_file.close()

    party = {
            'lines': party_lines,
            'nick': '-'.join(filename.split('-')[:-2]),
            'date': filename.split('-')[-2],
            'time': filename.split('-')[-1],
            }
    
    return bottle.template('tpl/party', party=party, network=network)


if __name__ == '__main__':
    bottle.run(host='0.0.0.0', port=8080)
else:
    application = bottle.default_app()
