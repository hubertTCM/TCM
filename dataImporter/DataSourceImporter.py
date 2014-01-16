﻿# -*- coding: utf-8 -*-
import os
import sys
def append_ancestors_to_system_path(levels):
    parent = os.path.dirname(__file__)
    for i in range(levels):
        sys.path.append(parent)
        parent = os.path.abspath(os.path.join(parent, ".."))

append_ancestors_to_system_path(2)

reload(sys)
os.environ.update({"DJANGO_SETTINGS_MODULE":"TCM.settings"})

from django.core.management import setup_environ
import TCM.settings
from TCM.models import *
setup_environ(TCM.settings)

class SourceImporter:
    def __init__(self):
        self._sourceInfoCreators = {}
        self._sourceInfoCreators[u'Book'] = self.__create_book_info__
        self._sourceInfoCreators[u'Web'] = self.__create_webInfo__
        
    def __create_webInfo__(self, sourceInfo):
        pass
         
    #{u'category': u'Book', u'name': u'范中林六经辨证医案'}                     
    def __create_book_info__(self, sourceInfo):
        book, isCreated = Book.objects.get_or_create(title = sourceInfo[u'name'])
        if (isCreated):
            book.category = u'Book'
            book.save()                    
        return book
    
    def import_source(self, sourceInfo):
        if (not u'category' in sourceInfo):
            return
        category = sourceInfo[u'category']
        if (category in self._sourceInfoCreators):
            return self._sourceInfoCreators[category](sourceInfo)
        return None
        