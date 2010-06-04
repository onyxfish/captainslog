import pymongo

import settings

mongo = pymongo.Connection()
db = mongo[settings.MONGO_DB]
db.drop_collection(settings.APACHE_ACCESS_COLLECTION)
db.drop_collection(settings.LOG_COLLECTION)
mongo.drop_database(settings.MONGO_DB)