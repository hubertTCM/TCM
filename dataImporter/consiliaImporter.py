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

from DataSourceImporter import *

from TCM.models import *
import TCM.settings
setup_environ(TCM.settings)

class SingleConsiliaImporter:
    def __init__(self, consilia):
        self._source_importer = SourceImporter()
        self._consiliaInfo = consilia
                    
        defaultInfo = {u'title': u'unknown', u'description' : None, u'creationTime' : None}
        Utility.apply_default_if_not_exist(self._consiliaInfo, defaultInfo)
        
        self._s_data_source = None
        
    def __run_action_when_key_exists__(self, key, action):
        return Utility.run_action_when_key_exists(key, self._consiliaInfo, action)
            
    def __create_author__(self, authorName):
        self._author = None 
        self._author, isCreated = Person.objects.get_or_create(name = authorName)
        if (isCreated):
            self._author.save()
                  
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
        self._consiliaSummary.comeFrom = self._s_data_source   
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
        self._s_data_source = self.__run_action_when_key_exists__(u'comeFrom', self._source_importer.import_source)
        
        self.__create_consilia__()
        
        # invoke after consilia is created            
        self.__run_action_when_key_exists__(u'diseaseName', self.__create_diseas_info__)          

class Importer:  
    def __init__(self):
        self._consiliaSources = []
        self._consiliaSources.append(Provider_fzl())
        self._consiliaSources.append(Provider_zmt())  
        
    def import_all_consilias(self):
        for provider in self._consiliaSources:
            for consilia in provider.get_all_consilias():
                try:
                    impoter = SingleConsiliaImporter(consilia)
                    impoter.upload_to_database()             
                except Exception,ex:
                    print "***" + str(consilia)
                    print Exception,":",ex
                    
if __name__ == "__main__":
    importerInstance = Importer()
    importerInstance.import_all_consilias()
    print 'done'