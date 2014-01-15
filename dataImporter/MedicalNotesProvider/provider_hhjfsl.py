# -*- coding: utf-8 -*-
import sys
import os
import codecs
import re

def append_ancestors_to_system_path(levels):
    parent = os.path.dirname(__file__)
    for i in range(levels):
        sys.path.append(parent)
        parent = os.path.abspath(os.path.join(parent, ".."))
        
append_ancestors_to_system_path(3)

from dataImporter.Utils.Utility import *
from dataImporter.Utils.WebUtil import *


# <tr class="tr3">
    # <td class="icon tar" width="30">
        # <a title="热门主题" href="read.php?tid=27008" target="_blank"><img src="images/wind85/thread/topichot.gif" align="absmiddle"></a>    
    # </td>
    # <td class="subject" id="td_27008">
        # <a href="read.php?tid=27008" name="readlink" id="a_ajax_27008" class="subject_t f14">向雅安灾民荐方</a>&nbsp;<span class="s2 w"></span><img src="images/wind85/file/new.gif" align="absmiddle" title="新帖" alt="新帖" />
    # </td>
    # <td class="author">
        # <a href="u.php?uid=27" class=" _cardshow" data-card-url="pw_ajax.php?action=smallcard&type=showcard&uid=27" target="_blank" data-card-key="黄煌">黄煌</a>
        # <p >2013-04-25</p>
    # </td>
    # <td class="num" width="60"><em>23</em>/841</td>
    # <td class="author">
        # <a href="u.php?username=ayabrea" target="_blank" class=" _cardshow" data-card-url="pw_ajax.php?action=smallcard&type=showcard&username=ayabrea" data-card-key="ayabrea">ayabrea</a>
        # <p><a href="read.php?tid=27008&page=e#a" title="2013-04-28 20:55">36分钟前</a></p>
    # </td>
# </tr>
class SummaryProvider:
    def __init__(self, url):
        self._rootUrl = url 
        self._config = {
                    'xpath':'//tr[@class="tr3"]',
                    'extract_attributes':[{'xpath':'./td[2]/a', 'target_attri_name':'title'},
                                          {'xpath':'./td[2]/a', 'source_attri' : 'href', 'target_attri_name':'source'},
                                          {'xpath':'./td[3]/p', 'target_attri_name':'create_time'},
                                          {'xpath':'./td[3]/a', 'source_attri' : 'href', 'target_attri_name':'author_uid_info'},
                                        ]
                }
        
    def __get_attribute_value__(self, attribute_name, dicts):
        url_dict = Utility.get_value('extract_attributes', dicts)
        return  Utility.get_value(attribute_name, url_dict)     
        
    def __get_page_count__(self, html_root):
        # <div class="pages">
            # <b>1</b>
            # <a href="thread.php?fid=30&page=2">2</a>
            # <a href="thread.php?fid=30&page=3">3</a>
        # </div>
        page_count_config = {
                            'xpath' : '//div[@class="pages"]/a',
                            'extract_attributes':[{'target_attri_name':'page_count'}] # root url http://www.hhjfsl.com/jfbbs
                        }
        items = web_extractor.get_values_from_html_tree(html_root, page_count_config)
        if (items is None):
            return 1
        
        page_counts = [self.__get_attribute_value__('page_count', provider) for provider in items if provider is not None]
        page_counts = Utility.remove_none_from(page_counts)
        
        page_count = 1
        for item in page_counts:
            current_page_count = int(item)
            if (current_page_count > page_count):
                page_count = current_page_count
        return page_count       
    
    def __get_summarys__(self, page_root):
        items = web_extractor.get_values_from_html_tree(page_root, self._config)
        if (items is None):
            return
        summarys = [Utility.get_value('extract_attributes', provider) for provider in items]
        summarys = Utility.remove_none_from(summarys)
        
        return summarys
    
    def get_summarys(self):
        root = web_extractor.get_html_root(self._rootUrl)
        page_count = self.__get_page_count__(root)
        page_index = 1
        #print page_count
        summarys = []
        while page_index <= page_count:
            page_url = self._rootUrl + "&page=" + str(page_index)
            if page_index == 1:
                summarys_from_page = self.__get_summarys__(root)
            else:
                summarys_from_page = self.__get_summarys__(web_extractor.get_html_root(page_url))
            page_index = page_index + 1
            
            if (summarys_from_page is None):
                continue
            summarys.extend(summarys_from_page)
            
        return summarys
    
p = SummaryProvider("http://www.hhjfsl.com/jfbbs/thread.php?fid=13")
p.get_summarys()
print "done"