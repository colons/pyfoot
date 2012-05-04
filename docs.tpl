<!DOCTYPE html>
<head lang="en">
<meta http-equiv="Content-Type" content="text/html; charset=UTF-8">
<title>!help | a pyfoot document</title>

<link rel="stylesheet" type="text/css" href="http://d.bldm.us/woof.css">
</head>

<body>
<h1>pyfoot</h1>

<p class="summary">A Python IRC robot. Source available on <a href="https://bitbucket.org/colons/pyfoot/">Bitbucket</a>.</p>

%if conf:
<div class="network section">
    <div class="heading">
        <h3>{{conf['network_address']}}</h3>
    </div>
    <div class="setting">
        <div class="key">
            <p>autojoin</p>
        </div>
        <div class="item">
            <p>{{!' <span class=separator>:span> '.join(conf['network_channels'])}}</p>
        </div>
    </div>
    <div class="setting">
        <div class="key">
            <p>admin</p>
        </div>
        <div class="item">
            <p>{{!' <span class=separator>:</span> '.join(conf['admin_admins'])}}</p>
        </div>
    </div>
</div>
%end

%for module in modules:
<div class="module section">
    <div class="heading">
        <h3>{{module['name']}}</h3>
    </div>
    %if module['blacklist']:
    <div class="blacklist">
        <div class="item">
            <p>disabled in {{!' <span class=separator>:</span> '.join(module['blacklist'])}}</p>
        </div>
    </div>
    %end
    %if module['docstring']:
    <div class="overview">
        <p>{{!module['docstring']}}</p>
    </div>
    %end
    %for function in module['functions']:
    <div class="command">
        <div class="usage">
            <p class="irc">{{function['command']}}</p>
        </div>
        <div class="docstring">
            {{!function['docstring']}}
        </div>
    </div>
    %end
</div>
%end
    
<div class="behavior section">
    <div class="heading">
        <h3>behaviour</h3>
    </div>
    <div class="item">
        <p>On startup, pyfoot will join all the channels his configuration suggests he should. Channels joined and left while running do not change this.
        <p>While running, he will join any channel he recieves an <a href="http://www.irchelp.org/irchelp/rfc/chapter4.html#c4_2_7">invitation</a> to. He may not be welcome, however, and there's no mechanism on his end for detaching from a channel.</p>
        <p>pyfoot will, under no circumstances, automatically rejoin a channel when kicked. If you want him back, re-invite him.</p>
    </div>
</div>
    
    <p class="credit">A <a href="http://www.musicfortheblind.co.uk/">Music for the Blind</a> production.</p>
</body>
