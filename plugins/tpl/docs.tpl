%rebase tpl/base title='%shelp' % conf['comchar'], network=conf['alias']

<p class="summary">A Python IRC robot. Source available on <a href="https://github.com/colons/pyfoot/">GitHub</a>.</p>

%if per_network and conf['alias'] != 'GLOBAL':
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

<div class="plugin_list section">
    <div class="heading">
        <h3>plugins</h3>
    </div>
    % for plugin in plugins:
    <div class="key">
        <p><a href="#{{plugin['name']}}">{{plugin['name']}}</a>
    </div>
    <div class="item">
        <p class="irc">
        % commands = [f['command'] for f in plugin['functions']]
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

%for plugin in plugins:
<div class="plugin section" id="{{plugin['name']}}">
    <div class="heading">
        <h3>{{plugin['name']}}</h3>
        %if plugin['blacklist']:
            <div class="blacklist item">
                <p>disabled in {{!' <span class="separator">:</span> '.join(plugin['blacklist'])}}</p>
            </div>
        %end
    </div>
    %if plugin['docstring']:
    <div class="overview">
        {{!plugin['docstring']}}
    </div>
    %end
    %for function in plugin['functions']:
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
        {{!behaviour}}
    </div>
</div>
