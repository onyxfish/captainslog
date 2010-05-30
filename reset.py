import pymongo

MONGO_DB = 'captainslog'
APACHE_ACCESS_COLLECTION = 'apache_access'
LOG_COLLECTION = 'logs'

mongo = pymongo.Connection()
db = mongo[MONGO_DB]
db.drop_collection(APACHE_ACCESS_COLLECTION)
db.drop_collection(LOG_COLLECTION)
mongo.drop_database(MONGO_DB)