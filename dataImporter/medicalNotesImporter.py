# -*- coding: utf-8 -*-
import os
import sys
from django.core.management import setup_environ

from MedicalNotesProvider.provider_hhjfsl import *
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

class MedicalNotesImporter:
    def __init__(self):
        self._providers = []
        self._providers.append(HHJFSLNotesProvider("http://www.hhjfsl.com/jfbbs/thread.php?fid=13"))
        
    def import_all(self):
        pass

i = MedicalNotesImporter()
i.import_all()