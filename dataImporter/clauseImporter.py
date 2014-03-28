# -*- coding: utf-8 -*-
import os
import sys
from django.core.management import setup_environ

from ClauseProvider.TreatiseOnFebrileDiseases import *
from ClauseProvider.GoldenChamber import *
from ClauseProvider.wbtb import wbtb_provider

from dataImporter.Utils.Utility import *
from dataImporter.Utils.HerbUtil import HerbUtility
from DataSourceImporter import *
from prescriptionImporter import *

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

class SingleClauseImporter:
    def __init__(self, clause_data):
        self._prescription_data = clause_data
        self._author_importer = PersonImporter()
        self._source_importer = SourceImporter()
        
    def __import_category__(self, clause):
        if not ('category' in self._prescription_data):
            return
        category, is_created = ClauseCategory.objects.get_or_create(name = self._prescription_data['category'])
        if is_created:
            category.save()
        
        reference, is_created = ClauseCategoryReference.objects.get_or_create(clause=clause, category=category)
        if is_created:
            reference.save()
            
    def __get_data_source__(self):
        come_from = None
        if 'comeFrom' in self._prescription_data:
            return self._prescription_data['comeFrom']
        return come_from
    
    def do_import(self):
#         clause = Clause()      
#         clause.comeFrom = Utility.run_action_when_key_exists(u'comeFrom', self._prescription_data, self._source_importer.import_source)
#         clause.content = self._prescription_data[u'content']
#         clause.index = self._prescription_data[u'index']
#         clause.save()
        
        prescriptions_importer = PrescriptionsImporter(self._prescription_data['prescriptions'])
        prescriptions_importer.do_import()
        
#         self.__import_category__(clause)


class Importer:
    def __init__(self):
        self._providers = []
        self._providers.append(FebribleDiseaseProvider())
        self._providers.append(GoldenChamberProvider())
        self._providers.append(wbtb_provider(None))
    
    def import_all_clauses(self):
        for source_provider in self._providers:
            for clause in source_provider.get_all_clauses():
                try:
                    importer = SingleClauseImporter(clause)
                    importer.do_import()                
                except Exception,ex:
                    print Exception,":",ex
    

if __name__ == "__main__":
    def process_all_components(process):
        importer = Importer()
        for source_provider in importer._providers:
            for clause in source_provider.get_all_clauses():
                for prescription in clause['prescriptions']:
                    for component in prescription['components']:
                        if process:
                            process(prescription, component)

    def check_unimported_herb():
        utility = HerbUtility()
        unimported_herbs = []
        def check_herb(prescription, component):
            herb_name = component['medical']
            if herb_name in unimported_herbs:
                return
            if not utility.is_herb(herb_name):
                unimported_herbs.append(herb_name)                             
                message = "herb " + herb_name + "   prescriptionName:" + prescription['name']
                if '_debug_source' in prescription:
                    message = message + "   source:"+prescription['_debug_source']                 
                print message
                
        process_all_components(check_herb)
        
    def check_unit():
        all_units = []
        def check_single_unit(prescription, component):
            unit = component['unit']
            if not unit or unit in all_units:
                return
                        
            herb_name = component['medical']
            all_units.append(unit)                            
            message = "unit: " + unit + "   prescriptionName:" + prescription['name'] + " herb: " + herb_name
            if '_debug_source' in prescription:
                message = message + "   source:"+prescription['_debug_source']                 
            print message
            
    def print_component_info(prescription, component):
        message = Utility.convert_dict_to_string(component) + " prescriptionName:" + prescription['name']
        if '_debug_source' in prescription:
            message = message + "   source:"+prescription['_debug_source']  
        print message
        
    process_all_components(print_component_info)
                
#     check_unimported_herb()
    check_unit()
    process_all_components(None)
    
#     importer = Importer()
#     importer.import_all_clauses()
    print "done"