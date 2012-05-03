<!DOCTYPE html>
<head lang="en">
<meta http-equiv="Content-Type" content="text/html; charset=UTF-8">
<title>!help | a pyfoot document</title>

<link rel="stylesheet" type="text/css" href="http://d.bldm.us/woof.css">
</head>

<body>
    <h1>pyfoot</h1>

    A useless, poorly documented<span class="ast">*</span> and badly written IRC robot. Python source available on <a href="https://bitbucket.org/colons/pyfoot/">Bitbucket</a>.

    <!--
    <h2>Features</h2>
    -->
    
%for module in modules:
<div class="module">
    <h3>{{module['name']}}</h3>
%if module['docstring']:
    <div class="overview">
        <p>{{!module['docstring']}}</p>
    </div>
%end
%for function in module['functions']:
    <div class="command">
        <div class="usage">
            {{function['command']}}
        </div>
        <div class="docstring">
            {{!function['docstring']}}
        </div>
    </div>
%end
</div>
%end
    
    <h2>Behaviour</h2>
    <p>On startup, pyfoot will join all the channels his configuration suggests he should. Channels joined and left while running do not change this.
    <p>While running, he will join any channel he recieves an <a href="http://www.irchelp.org/irchelp/rfc/chapter4.html#c4_2_7">invitation</a> to. He may not be welcome, however, and there's no mechanism on his end for detaching from a channel.</p>
    <p>pyfoot will, under no circumstances, automatically rejoin a channel when kicked. If you want him back, re-invite him.</p>
    
    <p class="credit">A <a href="http://www.musicfortheblind.co.uk/">Music for the Blind</a> production.</p>
    <p class="disclaimer">This document, which fails to cover maintenance and augmentation, doesn't count.</p>
</body>
