# -*- coding: utf-8 -*-
import codecs
import fnmatch
import os
import sys

def append_ancestors_to_system_path(levels):
    parent = os.path.dirname(__file__)
    for i in range(levels):
        sys.path.append(parent)
        parent = os.path.abspath(os.path.join(parent, ".."))
        
append_ancestors_to_system_path(3)
from dataImporter.Utils.WebUtil import *
from thirdParty.BeautifulSoup import BeautifulSoup

class Provider_zmt:
    def __init__(self):
        source_folder = os.path.dirname(__file__)
        source_folder = os.path.join(source_folder, "resources")#source_folder + 'resources\\zmt'
        source_folder = os.path.join(source_folder, "zmt")
        
        self._source_file_names = []
        for path, temp_dirs, files in os.walk(source_folder):
            for doc in [os.path.abspath(os.path.join(path, filename))
                    for filename in files 
                        if fnmatch.fnmatch(filename, "*.htm")]:
                self._source_file_names.append(doc)
                
                
    def __get_consilias_from__(self, root):
        index = 0
        consilias = []
        for item in root.findAll('li'):
            try:
                span = item.findAll('span')[0]
                title = span.string
                if not title:
                    title = span.contents[1]
            except:
                continue
            consilia = {u"author" : u"朱木通", u"title": title}
            
            for item in item.findAll('table'):
                index += 1
                '''
                The first 3 lines are you first want to see
                '''
                lineindex = 0
                
                temp = []
                for tritem in item.findAll('tr'): 
                    lineindex += 1
                    tditems = []
                    linecontent = ""
                    for tditem in tritem.findAll('td'):
                        tdcontent = tritem.string
                        if not tdcontent:
                            tdcontent = ''.join([e for e in tditem.recursiveChildGenerator() if isinstance(e, unicode)])
                        tditems.append(tdcontent)
                    linecontent = unicode(":".join(tditems))
                    if (lineindex < 3):
                        temp.append(linecontent)
                    if (lineindex == 2):
                        consilia[u'description'] = '\n'.join(temp)
                        temp = []
                    if (lineindex == 3):
                        consilia[u'details'] = []
                        consilia[u'details'].append({u"index" : 1, u"description" : linecontent})
                    if (lineindex == 4):
                        consilia_detail = consilia[u'details'][0]
                        consilia_detail[u'diagnosis'] = linecontent
                    if (lineindex > 4):
                        temp.append(linecontent)
                        
                consilia_detail = consilia[u'details'][0]
                consilia_detail[u'comments'] = '\n'.join(temp)
            consilias.append(consilia)
        return consilias
                           
    def get_all_consilias(self):
        consilias = []
        for file_name in self._source_file_names:
            print file_name
            source_file = codecs.open(file_name, 'r', 'big5', 'ignore')
            content = source_file.read()
            source_file.close()
            content = Utility.escape(content)
            root = BeautifulSoup(content)
            
            temp_consilias = self.__get_consilias_from__(root)
            for item in temp_consilias:
                item['debug_source'] = file_name
            consilias.extend(temp_consilias)
        return consilias
    
# temp = Provider_zmt()
# temp.get_all_consilias()
# print "zmt done"    
            