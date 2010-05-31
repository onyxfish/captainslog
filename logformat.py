import re

LOG_FORMATS = {
    '%a': '',   # Remote IP-address
    '%A': '',     # Local IP-address
    '%B': '(?P<bytes>[\d-]+)',     # Bytes sent, excluding HTTP headers.
    '%b': '(?P<bytes>[\d-]+)',     # Bytes sent, excluding HTTP headers.
    '%c': '',     # Connection status when response was completed.
    '%{FOOBAR}e': '',       # The contents of the environment variable FOOBAR
    '%f': '',     # Filename
    '%h': '(?P<host>[\d:\.]+)',     # Remote host
    '%H': '',     # The request protocol
    '%{FOOBAR}i': '',       # The contents of Foobar: header line(s) in the request sent to the server.
    '%l': '(?P<remote_log>.+)',     # Remote logname (from identd, if supplied)
    '%m': '',     # The request method
    '%{FOOBAR}n': '',       # The contents of note "Foobar" from another module.
    '%{FOOBAR}o': '',       # The contents of Foobar: header line(s) in the reply.
    '%p': '',     # The canonical Port of the server serving the request
    '%P': '',     # The process ID of the child that serviced the request.
    '%q': '',     # The query string (prepended with a ? if a query string exists)
    '%r': '(?P<verb>.*)\s(?P<path>.*)\s(?P<protocol>.*)',     # First line of request
    '%>s': '(?P<statuscode>[\d-]+)',    # Status of the last request (after any redirects)
    '%s': '',     # Status.  For requests that got internally redirected, this is the status of the *original* request
    '%t': '\[(?P<datetime>.*)\]',     # Time, in common log format time format (standard english format)
    '%T': '',     # The time taken to serve the request, in seconds.
    '%u': '(?P<auth_user>.+)',     # Remote user (from auth; may be bogus if return status (%s) is 401)
    '%U': '',     # The URL path requested, not including any query string.
    '%v': '',     # The canonical ServerName of the server serving the request.
    '%V': '',     # The server name according to the UseCanonicalName setting.
}

CLF_FORMAT = '%h %l %u %t \"%r\" %>s %b'
CLFV_FORMAT = '%v %h %l %u %t \"%r\" %>s %b'
NCSA_FORMAT = '%h %l %u %t \"%r\" %>s %b \"%{Referer}i\" \"%{User-agent}i\"'

def generate_format_regex(format_string):
    if format_string == 'CLF':
        format_string = CLF_FORMAT
    elif format_string == 'CLFV':
        format_string = CLFV_FORMAT
    elif format_string == 'NCSA':
        format_string = NCSA_FORMAT
            
    result = format_string
    
    for k, v in LOG_FORMATS.items():
        result = re.sub(k, v, result)
    
    result = '^%s$' % result
    
    return result