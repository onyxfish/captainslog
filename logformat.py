import re

LOG_FORMATS = {
    '%a': '(?P<remote_ip>.+)',   # Remote IP-address
    '%A': '(?P<local_ip>.+)',     # Local IP-address
    '%B': '(?P<bytes>[\d-]+)',     # Bytes sent, excluding HTTP headers.
    '%b': '(?P<bytes>[\d-]+)',     # Bytes sent, excluding HTTP headers.
    '%c': '(?P<connection>.+)',     # Connection status when response was completed.
    '%\{(.+)\}e': '(?P<env_\\1>.*)',       # The contents of the environment variable FOOBAR
    '%f': '(?P<filename>.+)',     # Filename
    '%h': '(?P<host>.+)',     # Remote host
    '%H': '(?P<protocol>.+)',     # The request protocol
    '%\{(.+?)\}i': '(?P<request_\\1>.*)',       # The contents of Foobar: header line(s) in the request sent to the server.
    '%l': '(?P<remote_log>.+)',     # Remote logname (from identd, if supplied)
    '%m': '(?P<verb>.+)',     # The request method
    '%\{(.+)\}n': '(?P<note_\\1>.*)',       # The contents of note "Foobar" from another module.
    '%\{(.+)\}o': '(?P<response_\\1>.*)',       # The contents of Foobar: header line(s) in the reply.
    '%p': '(?P<port>\d+)',     # The canonical Port of the server serving the request
    '%P': '(?P<pid>\d+)',     # The process ID of the child that serviced the request.
    '%q': '(?P<querystring>.+)',     # The query string (prepended with a ? if a query string exists)
    # TODO: these will conflict with individual params...
    '%r': '(?P<verb>.+) (?P<path>.+) (?P<protocol>.+)',     # First line of request
    '%>s': '(?P<statuscode>[\d-]+)',    # Status of the last request (after any redirects)
    '%s': '(?P<original_statuscode>[\d-]+)',     # Status.  For requests that got internally redirected, this is the status of the *original* request
    '%t': '\[(?P<datetime>.+)\]',     # Time, in common log format time format (standard english format)
    '%T': '(?P<time_to_serve>\d+)',     # The time taken to serve the request, in seconds.
    '%u': '(?P<auth_user>.+)',     # Remote user (from auth; may be bogus if return status (%s) is 401)
    '%U': '(?P<path>.+)',     # The URL path requested, not including any query string.
    # TODO: differentiate these?
    '%v': '(?P<server_name>.+)',     # The canonical ServerName of the server serving the request.
    '%V': '(?P<server_name>.+)',     # The server name according to the UseCanonicalName setting.
    
    # mod_logio
    '%I': '(?P<total_bytes_received>[\d-]+)',   # Bytes received, including request and headers, cannot be zero.
    '%O': '(?P<total_bytes_sent>[\d-]+)',   # Bytes sent, including headers, cannot be zero. 
}

CLF_FORMAT = '%h %l %u %t \"%r\" %>s %b'
CLFV_FORMAT = '%v %h %l %u %t \"%r\" %>s %b'
NCSA_FORMAT = '%h %l %u %t \"%r\" %>s %b \"%{Referer}i\" \"%{User-agent}i\"'

def get_format_regex(format_string):
    if format_string == 'CLF':
        format_string = CLF_FORMAT
    elif format_string == 'CLFV':
        format_string = CLFV_FORMAT
    elif format_string == 'NCSA':
        format_string = NCSA_FORMAT
            
    result = format_string
    
    for k, v in LOG_FORMATS.items():
        result = re.sub(k, v, result)
    
    # TODO: Bah, ugly hack for identifiers and spaces/tabs.
    result = re.sub('<(.+?)-(.+?)>', '<\\1_\\2>', result)
    result = '^%s$' % result
    
    return result