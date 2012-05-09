%rebase tpl/base title='%shelp' % conf['comchar']

<p class="summary">A Python IRC robot. Source available on <a href="https://bitbucket.org/colons/pyfoot/">Bitbucket</a>.</p>

%if per_network:
<div class="network section">
    <div class="heading">
        <h3>{{conf['network_address']}}</h3>
    </div>
    <div class="setting">
        <div class="key">
            <p>nick</p>
        </div>
        <div class="item">
            <p>{{conf['nick']}}
        </div>
    </div>
    <div class="setting">
        <div class="key">
            <p>autojoin</p>
        </div>
        <div class="item">
            <p>{{!' <span class="separator">:</span> '.join(conf['network_channels'])}}</p>
        </div>
    </div>
    <div class="setting">
        <div class="key">
            <p>admin</p>
        </div>
        <div class="item">
            <p>{{!' <span class="separator">:</span> '.join(conf['admin_admins'])}}</p>
        </div>
    </div>
    %if len(conf['nick_blacklist']) > 0:
    <div class="setting">
        <div class="key">
            <p>ignored</p>
        </div>
        <div class="item">
            <p>{{!' <span class="separator">:</span> '.join(conf['nick_blacklist'])}}</p>
        </div>
    </div>
    %end
</div>
%end

<div class="module_list section">
    <div class="heading">
        <h3>modules</h3>
    </div>
    % for module in modules:
    <div class="key">
        <p><a href="#{{module['name']}}">{{module['name']}}</a>
    </div>
    <div class="item">
        <p class="irc">
        % commands = [f['command'] for f in module['functions']]
        % for command in commands:
        {{command}}
            % if command != commands[-1]:
            <span class="separator"> | </span>
            % end
        % end
        </p>
    </div>
    % end
    </div>
</div>

%for module in modules:
<div class="module section" id="{{module['name']}}">
    <div class="heading">
        <h3>{{module['name']}}</h3>
        %if module['blacklist']:
            <div class="blacklist item">
                <p>disabled in {{!' <span class="separator">:</span> '.join(module['blacklist'])}}</p>
            </div>
        %end
    </div>
    %if module['docstring']:
    <div class="overview">
        {{!module['docstring']}}
    </div>
    %end
    %for function in module['functions']:
    <div class="command">
        <div class="usage key">
            <p class="irc">{{function['command']}}</p>
        </div>
        <div class="docstring item">
            {{!function['docstring']}}
        </div>
    </div>
    %end
</div>
%end
    
<div class="behaviour section">
    <div class="heading">
        <h3>behaviour</h3>
    </div>
    <div class="item">
        <p>On startup, {{conf['nick']}} will join all the channels his configuration suggests he should. Channels joined and left while running do not change this.
        <p>While running, he will join any channel he recieves an <a href="http://www.irchelp.org/irchelp/rfc/chapter4.html#c4_2_7">invitation</a> to. He will, under no circumstances, automatically rejoin a channel when kicked. If you want him back, re-invite him.</p>
    </div>
</div>
