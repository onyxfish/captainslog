from datetime import datetime
import os
import re
import time

import pymongo

import logformat
import settings

mongo = pymongo.Connection()
db = mongo[settings.MONGO_DB]
apache_access_collection = db[settings.APACHE_ACCESS_COLLECTION]
log_collection = db[settings.LOG_COLLECTION]

apache_access_collection.ensure_index([
    ('host', pymongo.ASCENDING),
    ('datetime', pymongo.DESCENDING),
    ('path', pymongo.ASCENDING), 
    ('statuscode', pymongo.ASCENDING)
]);

log_collection.ensure_index([('path', pymongo.ASCENDING)], unique=True);

# TODO: make configurable
log_config = {
    # '/Users/sk/src/captainslog/app1/apps.access.log': 'NCSA',
    # '/Users/sk/src/captainslog/app1/Medill.access.log': 'NCSA',
    '/Users/sk/src/captainslog/app1/homicides.access.log': '\[?%h\]? %l %u %t \"%r\" %>s %b \"%{Referer}i\" \"%{User-agent}i\" %I %O'
}

# TODO: load regexes dynamically from config
# CLF_REGEX = re.compile(logformat.get_format_regex('NCSA'))

logs = []
regexes = {}
log_files  = {}

for path, format in log_config.items():
    log = log_collection.find_one({'path': path})
    
    if not log:
        log = {
            'path': path,
            'type': 'apache_access',
            'last_byte': 0,
        }
        
        log['_id'] = log_collection.insert(log)
    
    regex = logformat.get_format_regex(format)
    print regex
    regexes[log['_id']] = re.compile(regex)
    
    log_files[log['_id']] = open(log['path'], 'r')
    log_files[log['_id']].seek(log['last_byte'])
    
    logs.append(log)

while 1:
    for log in logs:
        f = log_files[log['_id']]
        
        line = f.readline()
    
        while line:
            print line
            match = regexes[log['_id']].match(line)
            doc = match.groupdict()

            if 'datetime' in doc:
                # Date format: 28/May/2010:19:41:14 -0500
                # TODO - fix timezone
                doc['datetime'] = datetime.strptime(doc['datetime'][:-6], '%d/%b/%Y:%H:%M:%S')

            if 'bytes' in doc:
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