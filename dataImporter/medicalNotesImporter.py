# -*- coding: utf-8 -*-
import os
import sys
from django.core.management import setup_environ

from MedicalNotesProvider.provider_hhjfsl import *
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

import TCM.settings
from TCM.models import *

setup_environ(TCM.settings)

class SingleNoteImporter:
    def __init__(self, note_data):
        self._note_data = note_data        
        self._author_importer = PersonImporter()
        self._source_importer = SourceImporter()
    
    def __is_valid__(self):
        if (Utility.get_value('title', self._note_data) == None):
            return False
        return True
        
    def import_note(self):  
        if (not self.__is_valid__()):
            print "*invalid item" + str(self._note_data)
            return
        
        note = MedicalNote()      
        note.author = Utility.run_action_when_key_exists(u'author', self._note_data, self._author_importer.import_person)
        note.comeFrom = Utility.run_action_when_key_exists(u'comeFrom', self._note_data, self._source_importer.import_source)
        note.content = self._note_data[u'content']
        note.title = self._note_data[u'title']
        note.creationTime = Utility.get_value('creationTime', self._note_data)
        note.save()
        

class MedicalNotesImporter:
    def __init__(self):
        self._notes_source = []
        self._notes_source.append(HHJFSLNotesProvider(r"http://www.hhjfsl.com/jfbbs/thread.php?fid=13"))
        
    def import_all(self):
        for source_provider in self._notes_source:
            for note in source_provider.get_all_notes():
                try:
                    print "running"
                    importer = SingleNoteImporter(note)
                    importer.import_note()                
                except Exception,ex:
                    print Exception,":",ex
   
   
if __name__ == "__main__":      
    print "start"       
    i = MedicalNotesImporter()
    i.import_all()
    print "done"
