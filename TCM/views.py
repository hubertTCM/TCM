# -*- coding: utf-8 -*-
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.utils import simplejson
from TCM.models import *

class HTMLUtility:
    def convert_nl_to_html_format(content):
        return content.replace('\n', '<br/><br/>')
    convert_nl_to_html_format = staticmethod(convert_nl_to_html_format)           


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

def get_all_medical_notes(request):
    from_index = request.GET['from']
    to = request.GET['to']
    all_result = MedicalNote.objects.defer("content").order_by('-creationTime').all()
    all_summarys = all_result[from_index : to]
    summarys_json = [item.json() for item in all_summarys]
    json_object = {'totalCount' : all_result.count(), 'summarys' : summarys_json}
    return generate_json_response( json_object )


def get_medical_note_detail(request):
    note_id = request.GET['id']
    detail = MedicalNote.objects.get(id = note_id)
    json_object = detail.json()
    json_object['content'] = HTMLUtility.convert_nl_to_html_format(json_object['content'])
    return generate_json_response( json_object )

def save_medical_note(request):
    data = simplejson.loads(request.body)
    note_id = data[u'id']
    print 'id=' + str(note_id)
    content = data[u'content']
    print 'content=' + str(note_id)
    title = data[u'title']
    print 'title=' + str(note_id)
    if note_id <= 0:
        note = MedicalNote()
    else:
        note = MedicalNote.objects.get(id=note_id)
    
    note.content = content
    note.title = title
    note.save()
    return HttpResponse()