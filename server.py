from datetime import date, datetime, time, timedelta

import cherrypy
from mako.lookup import TemplateLookup
from mako.template import Template
import pymongo

MONGO_DB = 'captainslog'
APACHE_ACCESS_COLLECTION = 'apache_access'
LOG_COLLECTION = 'logs'

class CaptainsLog:
    def __init__(self):
        self.mongo = pymongo.Connection()
        self.db = self.mongo[MONGO_DB]
        self.apache_access_collection = self.db[APACHE_ACCESS_COLLECTION]
        self.log_collection = self.db[LOG_COLLECTION]
        
        self.templates = TemplateLookup(directories=['templates'], module_directory='/tmp/mako_modules')
    
    @cherrypy.expose
    def index(self, when='Today', host='All', path='All', statuscode='All'):
        q = {}
        
        if when == 'Today':
            today = datetime.combine(date.today(), time())
            q['when'] = { '$gt': today }
        else:
            # TODO
            pass

        if host == 'All':
            pass
        else:
            q['host'] = host

        if path == 'All':
            pass
        else:
            q['path'] = path

        if statuscode == 'All':
            pass
        else:
            q['statuscode'] = statuscode
            
        events = self.apache_access_collection.find(q)
        hosts = events.distinct('host')
        paths = events.distinct('path')
        statuscodes = events.distinct('statuscode')
        
        t = self.templates.get_template('index.html')
    
        return t.render(
            selected_when=when,
            hosts=hosts,
            selected_host=host,
            paths=paths,
            selected_path=path,
            statuscodes=statuscodes,
            selected_statuscode=statuscode,
            events=events,
            )

cherrypy.quickstart(CaptainsLog(), '/', 'cherrypy.conf')