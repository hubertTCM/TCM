# -*- coding: utf-8 -*-
import os
import sys
from django.core.management import setup_environ

from dataImporter.Utils.Utility import *

def append_ancestors_to_system_path(levels):
    parent = os.path.dirname(__file__)
    for i in range(levels):
        sys.path.append(parent)
        parent = os.path.abspath(os.path.join(parent, ".."))

append_ancestors_to_system_path(2)

reload(sys)
os.environ.update({"DJANGO_SETTINGS_MODULE":"TCM.settings"})


from TCM.models import *
import TCM.settings
setup_environ(TCM.settings)

class Adjustor:
    def adjust_medical_notes(self):
        for note in MedicalNote.objects.all():
            note.content = Utility.escape(note.content)
            note.save()

if __name__ == "__main__":
    a = Adjustor()
    a.adjust_medical_notes()
    print "done"