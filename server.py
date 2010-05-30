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
    def index(self, when='Today', host=None, path=None, statuscode=None):
        # NCSA format: host rfc931 username date:time request statuscode bytes
        hosts = self.collection.distinct('host')
        paths = self.collection.distinct('path')
        statuscodes = self.collection.distinct('statuscode')
    
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
            q['statuscode'] = statuscode
            
        events = self.collection.find(q)
        
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