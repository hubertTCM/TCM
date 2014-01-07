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
                self._diseas, isCreated = Disease.objects.get_or_create(name = diseasName)
                if (isCreated):
                    self._diseas.category = u'Modern'
                    self._diseas.save() 
               
    
        def uploadToDatabase(self):
            self.__runActionWhenKeyExists(u'author', self.__createAuthor__)
            self.__runActionWhenKeyExists(u'comeFrom', self.__createSource__)
            
            #
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