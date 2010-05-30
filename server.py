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
        # today = datetime.combine(date.today(), time())
        # tomorrow = today + timedelta(1)
        #     
        # total = self.collection.find().count()
        # events = self.collection.find().sort('when')
        
        #todays_events = collection.find({ 'when': { '$gt': today, '$lt': tomorrow}})
        
        # NCSA format: host rfc931 username date:time request statuscode bytes
        hosts = self.collection.distinct('host')
        paths = self.collection.distinct('path')
        statuscodes = self.collection.distinct('statuscode')
        
        t = self.templates.get_template('index.html')
    
        return t.render(
            hosts=hosts,
            paths=paths,
            statuscodes=statuscodes,
            )
            
    @cherrypy.expose
    def fetch(self, when='Today', host=None, path=None, statuscode=None):
        q = {}
        
        if when == 'Today':
            today = datetime.combine(date.today(), time())
            q['when'] = { '$gt': today }
        else:
            # TODO
            pass
            
        if host:
            q['host'] = host
            
        if path:
            q['path'] = path
            
        if statuscode:
            q['statuscode'] = int(statuscode)
            
        cherrypy.response.headers['Content-Type'] = "text/javascript"
        return str(list(self.collection.find(q)))

cherrypy.quickstart(CaptainsLog(), '/', 'cherrypy.conf')