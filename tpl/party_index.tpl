%rebase tpl/base title='parties'
<p class="summary"><a href="/help/{{network}}/">help</a>

<div class="section">
    <div class="heading">
        <h3>parties</h3>
    </div>
    %for party in parties:
    <div class="key">
        <p class='irc'>{{party['nick']}}</p>
    </div>
    <div class="item">
        <p>{{party['initial']}} <span class="separator">-&gt;</span> {{party['final']}}</p>
        <p><a href="{{party['url']}}">via {{party['length']-2}}</a></p>
    </div>
    %end
</div>
