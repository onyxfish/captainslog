from datetime import date, datetime, time, timedelta

import cherrypy
from mako.lookup import TemplateLookup
from mako.template import Template
import pymongo

import settings

count_map = '''
function() {
    emit(this.%s, { count: 1 });
}
'''

count_reduce = '''
function(key, values) {
    var total = 0;

    for ( var i=0; i< values.length; i++ ) {
        total += values[i].count;
    }
    
    return { count : total };
}
'''

class CaptainsLog:
    def __init__(self):
        self.mongo = pymongo.Connection()
        self.db = self.mongo[settings.MONGO_DB]
        self.apache_access_collection = self.db[settings.APACHE_ACCESS_COLLECTION]
        self.log_collection = self.db[settings.LOG_COLLECTION]
        
        self.templates = TemplateLookup(directories=['templates'], module_directory='/tmp/mako_modules')
    
    @cherrypy.expose
    def index(self, source='All', when='Today', host='All', path='All', statuscode='All', page='0', sort='when', sortdir='1'):
        q = {}

        if source == 'All':
            pass
        else:
            q['source'] = source
        
        if when == 'Today':
            today = datetime.combine(date.today(), time())
            q['datetime'] = { '$gt': today }
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
        whens = ['Today', 'This Week', 'This Month', 'This Year']
        sources = self.apache_access_collection.map_reduce(count_map % 'source', count_reduce, query=q).find().sort([('value.count', pymongo.DESCENDING)])
        hosts = self.apache_access_collection.map_reduce(count_map % 'host', count_reduce, query=q).find().sort([('value.count', pymongo.DESCENDING)])
        paths = self.apache_access_collection.map_reduce(count_map % 'path', count_reduce, query=q).find().sort([('value.count', pymongo.DESCENDING)])
        statuscodes = self.apache_access_collection.map_reduce(count_map % 'statuscode', count_reduce, query=q).find().sort([('value.count', pymongo.DESCENDING)])
        total_events = events.count()
        events = events.skip(int(page) * 20).limit(20).sort([(sort, int(sortdir))]);
        
        print hosts
        
        t = self.templates.get_template('index.html')
    
        return t.render(
            sources=sources,
            selected_source=source,
            whens=whens,
            selected_when=when,
            hosts=hosts,
            selected_host=host,
            paths=paths,
            selected_path=path,
            statuscodes=statuscodes,
            selected_statuscode=statuscode,
            total_events=total_events,
            events=events,
            page=page,
            sort=sort,
            sortdir=sortdir,
            )

cherrypy.quickstart(CaptainsLog(), '/', 'cherrypy.conf')