# -*- coding: utf-8 -*-
import os
import sys

from dataImporter.Utils.Utility import *
from dataImporter.Utils.HerbUtil import HerbUtility
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
    def __init__(self, prescription):
        self._prescription = prescription
        self._source_importer = SourceImporter()
        self._db_prescription_without_composition = None
        
    def __is_imported__(self):
        prescriptions = Prescription.objects.filter(name=self._prescription['name'])
        if len(prescriptions) == 0:
            return False
        current_components = self._prescription['components']
        for imported_prescription in prescriptions:
            herb_components = HerbComponent.objects.filter(prescription=imported_prescription)
            prescription_components = PrescriptionComponent.objects.filter(prescription=imported_prescription)
            
            imported_components_count = len(herb_components) + len(prescription_components)
            
            if imported_components_count == 0:
                self._db_prescription_without_composition = imported_prescription
            
            if imported_components_count != len(current_components):
                break
            
            is_same = True
            
            for item in current_components:
                if not herb_components.filter(component=item['medical']).exists() and not prescription_components.filter(component=item['medical']).exists():
                    is_same = False
                    break
            
            if is_same:
                return True
            
        return False    
        
    def __is_prescription_name__(self, name):
        known_medical_names = []
        known_medical_names.append(u'石膏')
        known_medical_names.append(u'铅丹')
        known_medical_names.append(u'牡丹')
        
        for medical in known_medical_names:
            if name.startswith(medical):
                return False
            
        if len(HerbAlias.objects.filter(name=name)) > 0 or len(HerbAlias.objects.filter(name=name)) > 0:
            return False
            
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

    def __get_unit__(self, name):   
        if not name:
            return None
                
        unit, is_created = HerbUnit.objects.get_or_create(name = name) 
        if is_created:
            unit.save()
        return unit
        
    def __get_herb__(self, name):
        herbs = Herb.objects.filter(name = name)
        if len(herbs) > 0:
            return herbs[0]
        
        alias = HerbAlias.objects.filter(name = name)
        if len(alias) > 0:
            return Herb.objects.get(name = alias[0].standardName.name)
            
        herb = Herb()
        herb.name = name
        herb.save()
        return herb
    
    def __get_prescription__(self, name):
        prescription, is_created = Prescription.objects.get_or_create(name = name)
        if is_created:
            prescription.comeFrom = Utility.run_action_when_key_exists(u'comeFrom', self._prescription, self._source_importer.import_source)
            prescription.save()
        return prescription
           
  
    def __import_composition__(self, db_prescription, component):
        try:
            medical_name = component['medical']
            if not self.__is_prescription_name__(medical_name):
                db_composition = HerbComponent()
                db_composition.component = self.__get_herb__(medical_name)
            else:
                db_composition = PrescriptionComponent()
                db_composition.component = self.__get_prescription__(medical_name)
                
            db_composition.prescription = db_prescription
            db_composition.quantity = component['quantity']
            db_composition.unit = self.__get_unit__(component['unit'])
            db_composition.comment = component['comments']
            db_composition.save()
                    
        except Exception,ex:
            print Exception,":",ex, "prescription: ",db_prescription.name, " medical: ",component['medical'], " quantity", component['quantity'], " unit", component['unit']
    
    def do_import(self):
        try:
            if self.__is_imported__():
                return

            if self._db_prescription_without_composition:
                db_prescription = self._db_prescription_without_composition
            else:
                db_prescription = Prescription()
                             
            db_prescription.category = 'Prescription'  
            db_prescription.comeFrom = Utility.run_action_when_key_exists(u'comeFrom', self._prescription, self._source_importer.import_source)
            db_prescription.comment = self._prescription['comment']        
            db_prescription.save()
            
            for component in self._prescription['components']:
                self.__import_composition__(db_prescription, component)   
                         
        except Exception,ex:
                print Exception,":",ex
    
class PrescriptionsImporter:
    def __init__(self, prescriptions):
        self._prescriptions = prescriptions
    
    def do_import(self):
        for prescription in self._prescriptions:
            importer = SinglePrescriptionImporter(prescription)
            importer.do_import()
            
if __name__ == "__main__":
    print "no data to import"