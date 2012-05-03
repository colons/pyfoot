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

def parse_paragraph(line, comchar):
    if comchar:
        line = line.replace('<comchar>', comchar)

    if line.startswith('$'):
        line = convert_mirc_entities(line)
        line = '<p class="input">%s</p>' % line[1:]

    elif line.startswith('>'):
        line = convert_mirc_entities(line)
        line = '<p class="output">%s</p>' % line[1:]
    else:
        line = '<p>%s</p>' % line

    return line



def examine_function(command, function, comchar):
    if function.__doc__:
        if comchar:
            command = comchar+command
        docstring = function.__doc__
        doc_lines = docstring.split('\n')

        explanation = []
        for line in [l.strip() for l in doc_lines if len(l.strip()) > 0]:
            explanation.append(parse_paragraph(line, comchar))

        docstring = '\n'.join(explanation)
        
        return {
            'command': command,
            'docstring': docstring,
            }


def get_entries(network):
    conf = config_module.Config(network)

    modules = []

    for modulename in conf.get('modules'):
        __import__('modules.'+modulename)
        module = sys.modules['modules.'+modulename]
        setattr(module.Module, 'name', modulename)
        modules.append(module.Module(None, conf))
        modules[-1].setDaemon(False)
    
    print modules

    entries = []

    for module in modules:
        functions = []

        if module.commands:
            for command, function in module.commands:
                entry = examine_function(command, function, conf.get('comchar'))
                if entry:
                    functions.append(entry)

        if module.regexes:
            for command, function in module.regexes:
                entry = examine_function(command, function, False)
                if entry:
                    functions.append(entry)

        
        module_dict = {
            'name': module.name,
            'functions': functions,
            }

        try:
            module_dict['docstring'] = module.__doc__.strip()
        except AttributeError:
            module_dict['docstring'] = None

        entries.append(module_dict)
        
    return entries

@bottle.route('/')

def index():
    entries = get_entries('nnchan')
    return bottle.template('docs', modules=entries)

bottle.run(host='localhost', port=8080)
# application = bottle.default_app()
