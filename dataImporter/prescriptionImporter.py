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

class SinglePrescriptionImporter:
    def __init__(self, prescription, source):
        self._prescription = prescription
        self._source = source
        self._source_importer = SourceImporter()
        
    def __get_component__(self, name):
        pass    
        
    def __import_composition__(self, db_prescription, component):
        db_composition = PrescriptionComposition()
        db_composition.component = self.__get_component__(component['medical'])
        db_composition.quantity = component['quantity']
        db_composition.unit = component['unit']
        db_composition.comment = component['comments']
        db_composition.save()
    
    def do_import(self):
        db_prescription = Prescription()    
        db_prescription.category = 'Prescription'  
        db_prescription.comeFrom = Utility.run_action_when_key_exists(u'comeFrom', self._source, self._source_importer.import_source)
        db_prescription.name = self._prescription['name']
        db_prescription.description = self._prescription['comment']        
        db_prescription.save()
        
        for component in self._prescription['components']:
            self.__import_composition__(db_prescription, component)
    
class PrescriptionImporter:
    def __init__(self, prescriptions, source):
        self._prescriptions = prescriptions
        self._source = source
    
    def do_import(self):
        for prescription in self._prescriptions:
            importer = SinglePrescriptionImporter(prescription, self._source)
            importer.do_import()
            
if __name__ == "__main__":
    print "no data to import"