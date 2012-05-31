* {
    padding: 0;
    margin: 0;
}

body {
    font-family: sans-serif;
    color: #333;

    background-color: #ddd;
    background-image: url('/static/noise.png');
    background-repeat: repeat;

    text-shadow: #eee 0px 1px 0;
    max-width: 800px;
    min-width: 400px;
    margin-left: auto;
    margin-right: auto;
    padding: 0 .5em;
}

h1 {
    font-weight: 500;
    padding: .8em 0;
    width: 78%;
    float: right;
}

h2 {
    clear: both;
    margin: 0;
    padding-bottom: .5em;
    padding-top: 2em;
    font-weight: 500;
    text-transform: lowercase;
    text-align: center;
}

h2:after {
    content: ' -';
}

h2:before {
    content: '- ';
}

div.heading {
    width: 20%;
    text-align: right;
    margin: 0;
    }

h3 {
    font-weight: 600;
}

p {
    margin: 0;
    padding: 0;
    font-size: .9em;
    padding-bottom: .4em;
}

p.summary {
    width: 78%;
    float: right;
    padding-bottom: 1.5em;
    clear: both;
}

a {
    color: {{pigment}};
    text-decoration: none;
}

a:hover {
    color: #333;
    border-color: {{pigment}};
    border-width: 0 0 1px 0;
    border-style: none none dotted none;
}

div.heading {
    padding-bottom: .5em;
}

div.section {
    clear: both;
    margin-bottom: 2em;
    overflow: auto;
}

p.irc, div.setting, div.blacklist p, span.irc {
    color: #777;
    font-family: monospace;
    font-size .9em;
}

div.blacklist {
    margin-bottom: -.6em;
}

span.separator {
    color: {{pigment}};
}

div.key {
    clear: both;
    float: left;
    text-align: right;
    width: 20%;
}

div.command, div.setting {
    clear: both;
}

div.docstring, div.overview, div.item {
    float: right;
    width: 78%;
    padding-bottom: 1em;
    clear: right;
}

p.input, p.output {
    font-family: monospace;
    margin-left: 1em;
    color: #666;
}

div.setting div.item {
    padding-bottom: 0;
}

div.plugin_list p, div.plugin_list div.item, div.plugin_list div.key {
    padding-bottom: .25em;
}

div.plugin_list div.item {
    padding-top: .1em;
}

div.plugin_list div.heading {
    margin-bottom: -.1em;
}

p.input:before {
    content: '$';
    color: {{pigment}};
    position: absolute;
    margin-left: -1em;
}

p.output:before {
    content: '>';
    color: {{pigment}};
    position: absolute;
    margin-left: -1em;
}

span.pigment {
    color: {{pigment}};
}

span.bold {
    font-weight: bold;
}

span.repl:before {
    content: '<'
}

span.repl:after {
    content: '>'
}

p.disclaimer {
    font-size: .7em;
    color: #777;
    padding: 0 0 1em 0;
    position: absolute;
    right: 1em;
}

p.disclaimer:before {
    content: '*';
    color: #999;
}

p.credit {
    clear: both;
    width: 78%;
    float: right;
    padding: 1em 0 2em 0;
    color: #666;
    font-size: .8em;
}
