# Mongodb
MONGO_DB = 'captainslog'
APACHE_ACCESS_COLLECTION = 'apache_access'
LOG_COLLECTION = 'logs'

# TODO: use this config...
# What logs should be parsed/tracked for analysis?
USER_LOGS = [
    # (path, type, format)
    # ('/var/log/apache2/access_log', 'apache_access', 'CLF'),
    # ('/Users/sk/src/captainslog/app1/apps.access.log', 'apache_access', 'NCSA'),
    # ('/Users/sk/src/captainslog/app1/reps.access.log', 'apache_access', '\[?%h\]? %l %u %t \"%r\" %>s %b \"%{Referer}i\" \"%{User-agent}i\" %I %O'),
    ('/Users/sk/src/captainslog/app1/homicides.access.log', 'apache_access', '\[?%h\]? %l %u %t \"%r\" %>s %b \"%{Referer}i\" \"%{User-agent}i\" %I %O'),
    ('/Users/sk/src/captainslog/app1/elections.access.log', 'apache_access', '\[?%h\]? %l %u %t \"%r\" %>s %b \"%{Referer}i\" \"%{User-agent}i\" %I %O'),
]

# What columns should be faceted for drill-down navigation?
FACET_COLUMNS = [
    'source',
    'datetime',
    'statuscode',
]

DISPLAY_COLUMNS = [
    'source',
    'datetime',
    'verb',
    'path',
    'statuscode',
    'bytes'
]