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
    def index(self, page='1', **kwargs):
        q = {}
    
        facets = []
        
        for column in settings.FACET_COLUMNS:
            f = { 'name': column, 'label': column.capitalize() }
            
            # Special casing for datetime facet
            if column == 'datetime':
                if column not in kwargs or kwargs[column] == 'Today':
                    today = datetime.combine(date.today(), time())
                    q['datetime'] = { '$gt': today }
                    f['selected'] = 'Today'
                elif kwargs[column] == 'Yesterday':
                    today = datetime.combine(date.today(), time())
                    yesterday = today - timedelta(1)
                    q['datetime'] = { '$gt': yesterday, '$lt': today }
                    f['selected'] = 'Yesterday'
            else:
                if column not in kwargs or kwargs[column] == 'All':
                    f['selected'] = 'All'
                else:
                    q[column] = kwargs[column]
                    f['selected'] = kwargs[column]
                
            facets.append(f)
                
        for f in facets:
            if f['name'] == 'datetime':
                # Fake out a mapreduce response for ease of display
                f['values'] = [{ '_id': 'Today', 'value': { 'count': None } }, { '_id': 'Yesterday', 'value': { 'count': None } }]
            else:
                f['values'] = self.apache_access_collection.map_reduce(count_map % f['name'], count_reduce, query=q).find().sort([('value.count', pymongo.DESCENDING)])
            
        events = self.apache_access_collection.find(q)
        # TODO: make rows-per-page configurable
        # NB: natural sort order is correct as datetime is always the 1st indexed column
        event_count = events.count()
        page = int(page)
        
        if event_count > 0:
            events = events.skip((page - 1) * 20).limit(20)
            page_count = (event_count / 20)
        else:
            page_count = 1
            
        print event_count
        print page_count
        print page
            
        t = self.templates.get_template('index.html')
    
        return t.render(
            settings=settings,
            facets=facets,
            events=events,
            page=page,
            page_count=page_count,
            )

cherrypy.quickstart(CaptainsLog(), '/', 'cherrypy.conf')