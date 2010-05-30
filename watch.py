from datetime import datetime
import os
import re
import time

import pymongo

# NCSA format: host rfc931 username date:time request statuscode bytes
NCSA_REGEX = re.compile('^(?P<host>[\d\.]+)\s(?P<rfc931>.+)\s(?P<username>.+)\s\[(?P<when>.*)\]\s"(?P<verb>.*)\s(?P<path>.*)\s(?P<protocol>.*)"\s(?P<statuscode>[\d-]+)\s(?P<bytes>[\d-]+)$')
LOG_PATH = '/var/log/apache2/access_log'

mongo = pymongo.Connection()
db = mongo['captainslog']
collection = db['apache']
collection.ensureIndex({'host':1, 'when':-1, 'path': 1, 'statuscode': 1});

f = open(LOG_PATH, 'r')
size = os.stat(LOG_PATH)[6]
f.seek(size)

while 1:
    line = f.readline()
    
    while line:
        match = NCSA_REGEX.match(line)
        doc = match.groupdict()

        # Date format: 28/May/2010:19:41:14 -0500
        # TODO - fix timezone
        doc['when'] = datetime.strptime(doc['when'][:-6], '%d/%b/%Y:%H:%M:%S')

        if doc['bytes'] == '-':
            doc['bytes'] = 0
        else:
            doc['bytes'] = int(doc['bytes'])
            
        doc['statuscode'] = int(doc['statuscode'])

        print collection.insert(doc)
        
        line = f.readline()
        
    time.sleep(10)