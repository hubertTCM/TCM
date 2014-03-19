# -*- coding: utf-8 -*-
import os
import sys
from django.core.management import setup_environ

from HerbProvider.HerbAliasProvider import HerbAliasProvider

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

class AliasImporter:
    def __init__(self):
        self._providers = []
        self._providers.append(HerbAliasProvider())
        
    def __import__(self, alias, standard_name):        
        herb, isCreated = Herb.objects.get_or_create(name=standard_name)
        if (isCreated):
            herb.save()  
        herb_alias = HerbAlias()
        herb_alias.name = alias
        herb_alias.standardName = herb
        herb_alias.save()
    
    def do_import(self):
        for source_provider in self._providers:
            for alias, standard_name in source_provider.get_all_alias_pair():
                try:
                    self.__import__(alias, standard_name)
                except Exception,ex:
                    print Exception,":",ex
    

if __name__ == "__main__":
    importer = AliasImporter()
    importer.do_import()
    print "done"