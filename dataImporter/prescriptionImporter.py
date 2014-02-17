# -*- coding: utf-8 -*-
import os
import sys

from dataImporter.Utils.Utility import *
from DataSourceImporter import *

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

class PrescriptionHelper:
    def is_prescription_name(name):
        prescription_end_tags = []
        prescription_end_tags.append(u'汤')
        prescription_end_tags.append(u'丸')
        prescription_end_tags.append(u'散')
        prescription_end_tags.append(u'膏')
        prescription_end_tags.append(u'丹')
        
        for item in prescription_end_tags:
            if (name.endswith(item)):
                return True
        
        return False
    
    is_prescription_name = staticmethod(is_prescription_name)  
    

class SinglePrescriptionImporter:
    def __init__(self, prescription, clause_data):
        self._prescription = prescription
        self._clause_data_dict = clause_data
        self._source_importer = SourceImporter()
        
    def __get_uni__t(self, name):   
        unit, is_created = HerbUnit.objects.get_or_create(name = name) 
        if is_created:
            unit.save()
        
    def __get_component__(self, name):
        if not PrescriptionHelper.is_prescription_name(name):
            herb, is_created = Herb.objects.get_or_create(name = name)
            if is_created:
                herb.category = 'Herb'
                herb.save()
                return herb
        
        return Prescription.objects.get(name = name)       
           
        
    def __import_composition__(self, db_prescription, component):
        db_composition = PrescriptionComposition()
        db_composition.component = self.__get_component__(component['medical'])
        db_composition.quantity = component['quantity']
        db_composition.unit = self.__get_uni__t(component['unit'])
        db_composition.comment = component['comments']
        db_composition.save()
    
    def do_import(self):
        db_prescription = Prescription()    
        db_prescription.category = 'Prescription'  
        db_prescription.comeFrom = Utility.run_action_when_key_exists(u'comeFrom', self._clause_data_dict, self._source_importer.import_source)
        db_prescription.name = self._prescription['name']
        db_prescription.description = self._prescription['comment']        
        db_prescription.save()
        
        for component in self._prescription['components']:
            self.__import_composition__(db_prescription, component)
    
class PrescriptionsImporter:
    def __init__(self, prescriptions, clause_data):
        self._prescriptions = prescriptions
        self._clause_data_dict = clause_data
    
    def do_import(self):
        for prescription in self._prescriptions:
            importer = SinglePrescriptionImporter(prescription, self._clause_data_dict)
            importer.do_import()
            
if __name__ == "__main__":
    print "no data to import"