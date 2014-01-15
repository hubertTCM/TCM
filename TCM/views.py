from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.utils import simplejson
from TCM.models import *


def generate_json_response(json_object):
    to_output = simplejson.dumps(json_object, ensure_ascii = False)
    return HttpResponse(to_output, mimetype = 'application/json')

def index(request):
    return render_to_response('index.html', {}, RequestContext(request, {}))

#very inefficient, should be updated later.
def get_all_consilias(request):
    from_index = request.GET['from']
    to = request.GET['to']
    all_result = ConsiliaSummary.objects.defer("description").order_by('-creationTime').all()
    all_summarys = all_result[from_index : to]
    summarys_json = [item.json() for item in all_summarys]
    json_object = {'totalCount' : all_result.count(), 'summarys' : summarys_json}
    return generate_json_response( json_object )

def get_consilia_detail(request):
    consilia_id = request.GET['id']
    print 'consilia_id = ' + str(consilia_id)
    summary = ConsiliaSummary.objects.get(id = consilia_id)
    json_object = summary.json()
    details = ConsiliaDetail.objects.filter(consilia = summary)
    json_object['details'] = [detail.json() for detail in details]
    return generate_json_response( json_object )