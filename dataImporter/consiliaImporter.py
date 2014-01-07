# -*- coding: utf-8 -*-
import os
import sys
from django.core.management import setup_environ

from ConsiliaProvider import provider_fzl
from dataImporter.Utils.Utility import *

def appendAncestorsToSystemPath(levels):
    parent = os.path.dirname(__file__)
    for i in range(levels):
        sys.path.append(parent)
        parent = os.path.abspath(os.path.join(parent, ".."))

appendAncestorsToSystemPath(2)

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
            self._sourceInfoCreators[u'Book'] = self.__createBookInfo__
            self._sourceInfoCreators[u'Web'] = self.__createWebInfo__
            
            defaultInfo = {u'title': u'unknown', u'description' : None, u'creationTime' : None}
            Utility.applyDefaultIfNotExist(self._consiliaInfo, defaultInfo)
            
        def __runActionWhenKeyExists(self, key, action):
            Utility.runActionWhenKeyExists(key, self._consiliaInfo, action)
                
        def __createAuthor__(self, authorName):
            self._author = None 
            self._author, isCreated = Person.objects.get_or_create(name = authorName)
            if (isCreated):
                self._author.save()
                
        def __createWebInfo__(self, sourceInfo):
            pass
             
        #{u'category': u'Book', u'name': u'范中林六经辨证医案'}                     
        def __createBookInfo__(self, sourceInfo):
            book, isCreated = Book.objects.get_or_create(title = sourceInfo[u'name'])
            if (isCreated):
                book.category = u'Book'
                book.save()                    
            return book
                
        #{'comeFrom': {u'category': u'Book', u'name': u'范中林六经辨证医案'}}        
        def __createSource__(self, sourceInfo):
            self._source = None
            if (not u'category' in sourceInfo):
                return
            category = sourceInfo[u'category']
            if (category in self._sourceInfoCreators):
                self._source = self._sourceInfoCreators[category](sourceInfo)
            
                
        # invoke this function when consilia object is ready            
        def __createDiseasInfo__(self, diseasNames):
            for diseasName in diseasNames:
                disease, isCreated = Disease.objects.get_or_create(name = diseasName)
                if (isCreated):
                    disease.category = u'Modern'
                    disease.save() 
                    
                diseaseConnection = ConsiliaDiseaseConnection()
                diseaseConnection.consilia = self._consiliaSummary
                diseaseConnection.disease = disease
                diseaseConnection.save()
                    
        def __createConsiliaSummary__(self):
            self._consiliaSummary = ConsiliaSummary()
            self._consiliaSummary.author = self._author
            self._consiliaSummary.comeFrom = self._source     
            self._consiliaSummary.title = self._consiliaInfo[u'title'] 
            self._consiliaSummary.description = self._consiliaInfo[u'description'] 
            self._consiliaSummary.creationTime = self._consiliaInfo[u'creationTime'] 
            self._consiliaSummary.save()
            
        def __createConsiliaDetail__(self, source):
            detail = ConsiliaDetail()
            detail.consilia = self._consiliaSummary
            detail.index = source[u'index']
            detail.description = source[u'description']
            detail.diagnosis = source[u'diagnosis']
            detail.comments = source[u'comments']
            detail.save()                
            
        def __createConsilia__(self):
            self.__createConsiliaSummary__()
            
            detailDefault = {u'description' : None, u'comments' : None}
            for sourceDetail in self._consiliaInfo[u'details']:
                Utility.applyDefaultIfNotExist(sourceDetail, detailDefault)
                self.__createConsiliaDetail__(sourceDetail)
               
        def uploadToDatabase(self):
            self.__runActionWhenKeyExists(u'author', self.__createAuthor__)
            self.__runActionWhenKeyExists(u'comeFrom', self.__createSource__)
            
            self.__createConsilia__()
            
            # invoke after consilia is created
            
            self.__runActionWhenKeyExists(u'diseaseName', self.__createDiseasInfo__)          
    
    def __init__(self):
        self._consiliaSources = []
        self._consiliaSources.append(provider_fzl.Provider_fzl())
        
    def importAllConsilias(self):
        for provider in self._consiliaSources:
            for consilia in provider.getAllConsilias():
                impoter = Importer.SingleConsiliaImporter(consilia)
                impoter.uploadToDatabase()

importerInstance = Importer()
importerInstance.importAllConsilias()
print 'done'