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

FACET_COLUMNS = [
    'host',
    # 'path',
    'statuscode',
]

class CaptainsLog:
    def __init__(self):
        self.mongo = pymongo.Connection()
        self.db = self.mongo[settings.MONGO_DB]
        self.apache_access_collection = self.db[settings.APACHE_ACCESS_COLLECTION]
        self.log_collection = self.db[settings.LOG_COLLECTION]
        
        self.templates = TemplateLookup(directories=['templates'], module_directory='/tmp/mako_modules')
    
    @cherrypy.expose
    def index(self, source='All', when='Today', page='0', sort='datetime', sortdir='1', **kwargs):
        q = {}

        if source == 'All':
            pass
        else:
            q['source'] = source
        
        if when == 'Today':
            today = datetime.combine(date.today(), time())
            q['datetime'] = { '$gt': today }
        elif when == 'Yesterday':
            today = datetime.combine(date.today(), time())
            yesterday = today - timedelta(1)
            q['datetime'] = { '$gt': yesterday, '$lt': today }
        
        facets = []
        
        for column in FACET_COLUMNS:
            f = { 'name': column, 'label': column.capitalize() }
            if column not in kwargs or kwargs[column] == 'All':
                f['selected'] = 'All'
            else:
                q[column] = kwargs[column]
                f['selected'] = kwargs[column]
                
            facets.append(f)
                
        for f in facets:
            f['values'] = self.apache_access_collection.map_reduce(count_map % f['name'], count_reduce, query=q).find().sort([('value.count', pymongo.DESCENDING)])
            
        events = self.apache_access_collection.find(q)
        whens = ['Today', 'Yesterday']
        sources = self.apache_access_collection.map_reduce(count_map % 'source', count_reduce, query=q).find().sort([('value.count', pymongo.DESCENDING)])
        total_events = events.count()
        events = events.skip(int(page) * 20).limit(20).sort([(sort, int(sortdir))]);
        
        t = self.templates.get_template('index.html')
    
        return t.render(
            sources=sources,
            selected_source=source,
            whens=whens,
            selected_when=when,
            facets=facets,
            total_events=total_events,
            events=events,
            page=page,
            sort=sort,
            sortdir=sortdir,
            )

cherrypy.quickstart(CaptainsLog(), '/', 'cherrypy.conf')