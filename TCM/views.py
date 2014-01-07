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

def get_all_consilias(request):
    all_summarys = ConsiliaSummary.objects.defer("description").order_by('-creationTime').all()
    json_object = [generate_json_response(dir(item)) for item in all_summarys]
    return generate_json_response( json_object )