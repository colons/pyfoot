from random import choice
import urllib

user_agents = [
    'Mozilla/5.0 (Windows; U; Windows NT 5.1; it; rv:1.8.1.11) Gecko/20071127 Firefox/2.0.0.11',
    'Opera/9.25 (Windows NT 5.1; U; en)',
    'Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; .NET CLR 1.1.4322; .NET CLR 2.0.50727)',
    'Mozilla/5.0 (compatible; Konqueror/3.5; Linux) KHTML/3.5.5 (like Gecko) (Kubuntu)',
    'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.8.0.12) Gecko/20070731 Ubuntu/dapper-security Firefox/1.5.0.12',
    'Lynx/2.8.5rel.1 libwww-FM/2.14 SSL-MM/1.4.1 GNUTLS/1.2.9'
]
html_types = ['text/html','application/xhtml+xml']
redirect_codes = [301,302,303]

"""Copied verbatim from BaseHTTPServer.BaseHTTPRequestHandler.responses"""
responses = {
        200: ('OK', 'Request fulfilled, document follows'),
        201: ('Created', 'Document created, URL follows'),
        202: ('Accepted', 'Request accepted, processing continues off-line'),
        203: ('Non-Authoritative Information', 'Request fulfilled from cache'),
        204: ('No Content', 'Request fulfilled, nothing follows'),
        205: ('Reset Content', 'Clear input form for further input.'),
        206: ('Partial Content', 'Partial content follows.'),
        400: ('Bad Request', 'Bad request syntax or unsupported method'),
        401: ('Unauthorized', 'No permission -- see authorization schemes'),
        402: ('Payment Required', 'No payment -- see charging schemes'),
        403: ('Forbidden', 'Request forbidden -- authorization will not help'),
        404: ('Not Found', 'Nothing matches the given URI'),
        405: ('Method Not Allowed', 'Specified method is invalid for this resource.'),
        406: ('Not Acceptable', 'URI not available in preferred format.'),
        407: ('Proxy Authentication Required', 'You must authenticate with this proxy before proceeding.'),
        408: ('Request Timeout', 'Request timed out; try again later.'),
        409: ('Conflict', 'Request conflict.'),
        410: ('Gone', 'URI no longer exists and has been permanently removed.'),
        411: ('Length Required', 'Client must specify Content-Length.'),
        412: ('Precondition Failed', 'Precondition in headers is false.'),
        413: ('Request Entity Too Large', 'Entity is too large.'),
        414: ('Request-URI Too Long', 'URI is too long.'),
        415: ('Unsupported Media Type', 'Entity body in unsupported format.'),
        416: ('Requested Range Not Satisfiable', 'Cannot satisfy request range.'),
        417: ('Expectation Failed', 'Expect condition could not be satisfied.'),
        100: ('Continue', 'Request received, please continue'),
        101: ('Switching Protocols', 'Switching to new protocol; obey Upgrade header'),
        300: ('Multiple Choices', 'Object has several resources -- see URI list'),
        301: ('Moved Permanently', 'Object moved permanently -- see URI list'),
        302: ('Found', 'Object moved temporarily -- see URI list'),
        303: ('See Other', 'Object moved -- see Method and URL list'),
        304: ('Not Modified', 'Document has not changed since given time'),
        305: ('Use Proxy', 'You must use proxy specified in Location to access this resource.'),
        307: ('Temporary Redirect', 'Object moved temporarily -- see URI list'),
        500: ('Internal Server Error', 'Server got itself in trouble'),
        501: ('Not Implemented', 'Server does not support this operation'),
        502: ('Bad Gateway', 'Invalid responses from another server/proxy.'),
        503: ('Service Unavailable', 'The server cannot process the request due to a high load'),
        504: ('Gateway Timeout', 'The gateway server did not receive a timely response'),
        505: ('HTTP Version Not Supported', 'Cannot fulfill request.')
}

def choose_agent():
    return choice(user_agents)

def ajax_url(url):
    """AJAX HTML Snapshot URL parsing"""
    """ https://developers.google.com/webmasters/ajax-crawling/docs/specification """
    hashbang_index = url.find('#!')
    if hashbang_index != -1:
        base = url[:hashbang_index]
        if '?' in base:
            join = '&'
        else:
            join = '?'
        url = base + join + '_escaped_fragment_=' + urllib.quote(url[hashbang_index+2:], '=')
    return url
