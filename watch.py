from datetime import datetime
import os
import re
import time

import pymongo

MONGO_DB = 'captainslog'
APACHE_ACCESS_COLLECTION = 'apache_access'
LOG_COLLECTION = 'logs'

# NCSA format: host rfc931 username date:time request statuscode bytes
NCSA_REGEX = re.compile('^(?P<host>[\d:\.]+)\s(?P<rfc931>.+)\s(?P<username>.+)\s\[(?P<when>.*)\]\s"(?P<verb>.*)\s(?P<path>.*)\s(?P<protocol>.*)"\s(?P<statuscode>[\d-]+)\s(?P<bytes>[\d-]+)$')

mongo = pymongo.Connection()
db = mongo[MONGO_DB]
apache_access_collection = db[APACHE_ACCESS_COLLECTION]
log_collection = db[LOG_COLLECTION]

apache_access_collection.ensure_index([
    ('host', pymongo.ASCENDING),
    ('when', pymongo.DESCENDING),
    ('path', pymongo.ASCENDING), 
    ('statuscode', pymongo.ASCENDING)
]);

log_collection.ensure_index([('path', pymongo.ASCENDING)], unique=True);

# TODO: make configurable
log_paths = ['/var/log/apache2/access_log']

logs = []
log_files  = {}

for path in log_paths:
    log = log_collection.find_one({'path':path})
    
    if not log:
        log = {
            'path': path,
            'type': 'apache_access',
            'last_byte': 0,
        }
        
        log['_id'] = log_collection.insert(log)
    
    log_files[log['_id']] = open(log['path'], 'r')
    log_files[log['_id']].seek(log['last_byte'])
    
    logs.append(log)

while 1:
    for log in logs:
        f = log_files[log['_id']]
        
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
                
            doc['source'] = log['path']

            print apache_access_collection.insert(doc)
        
            log['last_byte'] = f.tell()
            log_collection.save(log)
        
            line = f.readline()
        
    time.sleep(10)