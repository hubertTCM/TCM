# -*- coding: utf-8 -*-
import os
import sys
from django.core.management import setup_environ

from HerbProvider.HerbAliasProvider import HerbAliasProvider
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

class KnownAliasProvider:
    def get_all_alias_pair(self):
        items = [(ur"飞滑石", ur"滑石"),
                 (ur"大附子", ur"附子"),
                (ur"生附子", ur"附子"),
                (ur"生石膏", ur"石膏"),
                (ur"生白芍", ur"白芍"),
                (ur"生牡蛎", ur"牡蛎"),
                (ur"真阿胶", ur"阿胶"),
                (ur"鲜竹叶心", ur"竹叶"),
                (ur"竹叶心", ur"竹叶"),
                (ur"北秦皮", ur"秦皮"),
                (ur"生黄柏", ur"黄柏"),
                (ur"黄檗", ur"黄柏"),
                (ur"公丁香", ur"丁香"),
                (ur"倭硫黄", ur"硫黄"),
                (ur"生茅术",ur"苍术"),
                (ur"木香汁", ur"木香"),
                (ur"生 香附", ur"香附"),
                (ur"舶上硫黄", ur"硫黄"),
                (ur"云 茯苓", ur"茯苓"),
                (ur"茯苓块", ur"茯苓"),
                (ur"广皮", ur"陈皮"),
                (ur"橘皮", ur"陈皮"),
                (ur"桂枝木", ur"桂枝"),
                (ur"安南桂", ur"肉桂"),
                (ur"片子姜黄 ", ur"姜黄"),
                (ur"苏子霜 ", ur"苏子"),
                (ur"香附米 ", ur"香附"),
                (ur"青木香 ", ur"木香"),
                (ur"白粳米 ", ur"粳米"),
                (ur"乌扇 ", ur"射干"),
                (ur"苁蓉", ur"肉苁蓉"),
                (ur"香豆豉", ur"豆豉"),
                (ur"肥栀子", ur"栀子"),
                (ur"干苏叶", "苏叶"),
                # may lost information
                (ur"生竹茹", "竹茹"),
                ("生地黄汁", "生地"), 
                (ur"黑山栀", "栀子"),
                (ur"楂炭", ur"山楂"),
                (ur"蒲黄炭", ur"蒲黄"),
                (ur"鲜扁豆花", ur"扁豆花"),
                (ur"鲜荷叶边", ur"荷叶边"),
                (ur"鲜银花", ur"银花"),
                (ur"细生地", ur"生地"),
                (ur"生龟板", ur"龟板"),
                (ur"炙龟板", ur"龟板"),
                (ur"生白术", ur"白术"),
                (ur"炙黄芪", ur"黄芪"),
                (ur"藏红花", ur"红花"),
                (ur"川椒炭", ur"蜀椒"), 
                (ur"当归尾", ur"当归"),
                (ur"小茴香炭", ur"小茴香"),
                (ur"降香末", ur"降香"),
                (ur"枳实汁", ur"枳实"),
                (ur"姜汁", ur"生姜"), 
                (ur"卜子", ur"莱菔子"),
                 ]
        return items

class AliasImporter:
    def __init__(self):
        self._providers = []
        self._providers.append(HerbAliasProvider())
        self._providers.append(KnownAliasProvider())
        
    def __import__(self, alias, standard_name):
        alias = Utility.remove_blank_space(alias)
        standard_name = Utility.remove_blank_space(standard_name)   
        items = HerbAlias.objects.filter(name = alias)
        if len(items) > 0:
            return   
        
        print "importing " + alias
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