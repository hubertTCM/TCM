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

class KnownAliasProvider:
    def get_all_alias_pair(self):
        items = [(ur"飞滑石", ur"滑石"),
                (ur"生附子", ur"附子"),
                (ur"生石膏", ur"石膏"),
                (ur"生白芍", ur"白芍"),
                (ur"藏红花", ur"红花"),
                (ur"生牡蛎", ur"牡蛎"),
                (ur"真阿胶", ur"阿胶"),
                (ur"鲜竹叶心", ur"竹叶"),
                (ur"北秦皮", ur"秦皮"),
                (ur"生黄柏", ur"黄柏"),
                (ur"公丁香", ur"丁香"),
                (ur"倭 硫黄", ur"硫黄")
                 ]
        return items

class AliasImporter:
    def __init__(self):
        self._providers = []
        self._providers.append(HerbAliasProvider())
        self._providers.append(KnownAliasProvider())
        
    def __import__(self, alias, standard_name):   
        items = HerbAlias.objects.filter(name = alias)
        if len(items) > 0:
            print alias , " is imported"
            return   
        
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
    print "start"
    importer = AliasImporter()
    importer.do_import()
    print "done"