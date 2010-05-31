from datetime import date, datetime, time, timedelta

import cherrypy
from mako.lookup import TemplateLookup
from mako.template import Template
import pymongo

import settings

class CaptainsLog:
    def __init__(self):
        self.mongo = pymongo.Connection()
        self.db = self.mongo[settings.MONGO_DB]
        self.apache_access_collection = self.db[settings.APACHE_ACCESS_COLLECTION]
        self.log_collection = self.db[settings.LOG_COLLECTION]
        
        self.templates = TemplateLookup(directories=['templates'], module_directory='/tmp/mako_modules')
    
    @cherrypy.expose
    def index(self, source='All', when='Today', host='All', path='All', statuscode='All'):
        q = {}

        if source == 'All':
            pass
        else:
            q['source'] = source
        
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
        sources = events.distinct('source')
        hosts = events.distinct('host')
        paths = events.distinct('path')
        statuscodes = events.distinct('statuscode')
        
        t = self.templates.get_template('index.html')
    
        return t.render(
            selected_source=source,
            sources=sources,
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