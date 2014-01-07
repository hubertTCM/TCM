from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.utils import simplejson
from TCM.models import *

def generate_json_response(json_objects):
    to_output = simplejson.dumps(json_objects, ensure_ascii = False)
    return HttpResponse(to_output, mimetype = 'application/json')

def index(request):
    return render_to_response('index.html', {}, RequestContext(request, {}))

def getAllConsilias(request):
    allSummarys = ConsiliaSummary.objects.defer("description").order_by('-creationTime').all()
    jsonObject = []
    return generate_json_response( jsonObject )