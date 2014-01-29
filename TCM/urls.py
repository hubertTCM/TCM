import os

from django.conf.urls import patterns, include, url
from django.conf import settings
from views import *
# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'TCM.views.home', name='home'),
    # url(r'^TCM/', include('TCM.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # url(r'^admin/', include(admin.site.urls)),'',
    
    (r'^$', index), 
    (r'^lib/(?P<path>.*)$', 'django.views.static.serve', \
            {'document_root': settings.STATIC_PATH}),
    (r'^templates/(?P<path>.*)$', 'django.views.static.serve', \
            {'document_root': os.path.join('.', 'templates')}),
                       
    url(r'^allConsilias/', get_all_consilias),
    url(r'^consiliaDetail/', get_consilia_detail),
    
    url(r'^allMedicalNotes/', get_all_medical_notes),
    url(r'^medicalNoteDetail/', get_medical_note_detail),
    url(r'^saveMedicalNote/', save_medical_note),
)
