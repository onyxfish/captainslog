from datetime import date, datetime, time, timedelta

import cherrypy
from mako.lookup import TemplateLookup
from mako.template import Template
import pymongo

class CaptainsLog:
    def __init__(self):
        self.mongo = pymongo.Connection()
        self.db = self.mongo['captainslog']
        self.collection = self.db['apache']
        
        self.templates = TemplateLookup(directories=['templates'], module_directory='/tmp/mako_modules')
    
    @cherrypy.expose
    def index(self):
        today = datetime.combine(date.today(), time())
        tomorrow = today + timedelta(1)
    
        total = self.collection.find().count()
        events = self.collection.find().sort('when')
        
        #todays_events = collection.find({ 'when': { '$gt': today, '$lt': tomorrow}})
        
        t = self.templates.get_template('index.html')
    
        return t.render(
            events=events,
            total=total
            )

cherrypy.quickstart(CaptainsLog(), '/', 'cherrypy.conf')