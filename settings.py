# Mongodb
MONGO_DB = 'captainslog'
APACHE_ACCESS_COLLECTION = 'apache_access'
LOG_COLLECTION = 'logs'

# TODO: use this config...
# What logs should be parsed/tracked for analysis?
USER_LOGS = [
    # (path, type, format)
    ('/var/log/apache2/access_log', 'apache_access', 'CLF')
]

# What columns should be faceted for drill-down navigation?
FACET_COLUMNS = [
    'host',
    # 'path',
    'statuscode',
]