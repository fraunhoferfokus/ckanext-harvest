
from pylons import request
from ckan import logic
from ckan import model
import ckan.lib.helpers as h
import ckan.plugins as p

from ckanext.harvest.model import UPDATE_FREQUENCIES
from ckanext.harvest.plugin import DATASET_TYPE_NAME


def package_list_for_source(source_id):
    '''
    Creates a dataset list with the ones belonging to a particular harvest
    source.

    It calls the package_list snippet and the pager.
    '''
    limit = 20
    page = int(request.params.get('page', 1))
    fq = 'harvest_source_id:{0}'.format(source_id)
    search_dict = {
        'fq' : fq,
        'rows': 10,
        'sort': 'metadata_modified desc',
        'start': (page - 1) * limit,
    }

    context = {'model': model, 'session': model.Session}
    query = logic.get_action('package_search')(context, search_dict)

    base_url = h.url_for('{0}_read'.format(DATASET_TYPE_NAME), id=source_id)
    def pager_url(q=None, page=None):
        url = base_url
        if page:
            url += '?page={0}'.format(page)
        return url

    pager = h.Page(
        collection=query['results'],
        page=page,
        url=pager_url,
        item_count=query['count'],
        items_per_page=limit
    )
    pager.items = query['results']

    out = h.snippet('snippets/package_list.html', packages=query['results'])
    out += pager.pager()

    return out

def harvesters_info():
    context = {'model': model, 'user': p.toolkit.c.user or p.toolkit.c.author}
    return logic.get_action('harvesters_info_show')(context,{})

def harvester_types():
    harvesters = harvesters_info()
    return [{'text': p.toolkit._(h['title']), 'value': h['name']}
            for h in harvesters]

def harvest_frequencies():

    return [{'text': p.toolkit._(f.title()), 'value': f}
            for f in UPDATE_FREQUENCIES]