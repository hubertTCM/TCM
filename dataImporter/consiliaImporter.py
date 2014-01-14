# -*- coding: utf-8 -*-
import os
import sys
from django.core.management import setup_environ

from ConsiliaProvider.provider_fzl import *
from ConsiliaProvider.zmt import *
from dataImporter.Utils.Utility import *

def append_ancestors_to_system_path(levels):
    parent = os.path.dirname(__file__)
    for i in range(levels):
        sys.path.append(parent)
        parent = os.path.abspath(os.path.join(parent, ".."))

append_ancestors_to_system_path(2)

reload(sys)
os.environ.update({"DJANGO_SETTINGS_MODULE":"TCM.settings"})

import TCM.settings
from TCM.models import *

setup_environ(TCM.settings)

class Importer:
    class SingleConsiliaImporter:
        def __init__(self, consilia):
            self._consiliaInfo = consilia
            
            self._sourceInfoCreators = {}
            self._sourceInfoCreators[u'Book'] = self.__create_book_info__
            self._sourceInfoCreators[u'Web'] = self.__create_webInfo__
            
            defaultInfo = {u'title': u'unknown', u'description' : None, u'creationTime' : None}
            Utility.apply_default_if_not_exist(self._consiliaInfo, defaultInfo)
            
            self._source = None
            
        def __run_action_when_key_exists__(self, key, action):
            Utility.run_action_when_key_exists(key, self._consiliaInfo, action)
                
        def __create_author__(self, authorName):
            self._author = None 
            self._author, isCreated = Person.objects.get_or_create(name = authorName)
            if (isCreated):
                self._author.save()
                
        def __create_webInfo__(self, sourceInfo):
            pass
             
        #{u'category': u'Book', u'name': u'范中林六经辨证医案'}                     
        def __create_book_info__(self, sourceInfo):
            book, isCreated = Book.objects.get_or_create(title = sourceInfo[u'name'])
            if (isCreated):
                book.category = u'Book'
                book.save()                    
            return book
                
        #{'comeFrom': {u'category': u'Book', u'name': u'范中林六经辨证医案'}}        
        def __create_source__(self, sourceInfo):
            self._source = None
            if (not u'_source_foldery' in sourceInfo):
                return
            category = sourceInfo[u'category']
            if (category in self._sourceInfoCreators):
                self._source = self._sourceInfoCreators[category]
            
                
        # invoke this function when consilia object is ready            
        def __create_diseas_info__(self, diseasNames):
            for diseasName in diseasNames:
                disease, isCreated = Disease.objects.get_or_create(name = diseasName)
                if (isCreated):
                    disease.category = u'Modern'
                    disease.save() 
                    
                diseaseConnection = ConsiliaDiseaseConnection()
                diseaseConnection.consilia = self._consiliaSummary
                diseaseConnection.disease = disease
                diseaseConnection.save()
                    
        def __create_consilia_summary__(self):
            self._consiliaSummary = ConsiliaSummary()
            self._consiliaSummary.author = self._author
            self._consiliaSummary.comeFrom = self._source     
            self._consiliaSummary.title = self._consiliaInfo[u'title'] 
            self._consiliaSummary.description = self._consiliaInfo[u'description'] 
            self._consiliaSummary.creationTime = self._consiliaInfo[u'creationTime'] 
            self._consiliaSummary.save()
            
        def __create_consilia_detail__(self, source):
            detail = ConsiliaDetail()
            detail.consilia = self._consiliaSummary
            detail.index = source[u'index']
            detail.description = source[u'description']
            detail.diagnosis = source[u'diagnosis']
            detail.comments = source[u'comments']
            detail.save()                
            
        def __create_consilia__(self):
            self.__create_consilia_summary__()
            
            detailDefault = {u'description' : None, u'comments' : None}
            for sourceDetail in self._consiliaInfo[u'details']:
                Utility.apply_default_if_not_exist(sourceDetail, detailDefault)
                self.__create_consilia_detail__(sourceDetail)
               
        def upload_to_database(self):
            self.__run_action_when_key_exists__(u'author', self.__create_author__)
            self.__run_action_when_key_exists__(u'comeFrom', self.__create_source__)
            
            self.__create_consilia__()
            
            # invoke after consilia is created            
            self.__run_action_when_key_exists__(u'diseaseName', self.__create_diseas_info__)          
    
    def __init__(self):
        self._consiliaSources = []
        self._consiliaSources.append(Provider_fzl())
        self._consiliaSources.append(Provider_zmt())
        
    def import_all_consilias(self):
        for provider in self._consiliaSources:
            for consilia in provider.get_all_consilias():
                impoter = Importer.SingleConsiliaImporter(consilia)
                impoter.upload_to_database()

importerInstance = Importer()
importerInstance.import_all_consilias()
print 'done'