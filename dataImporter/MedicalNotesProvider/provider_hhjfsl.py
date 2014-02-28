# -*- coding: utf-8 -*-
import datetime
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

class PageProvider:
    def __init__(self, url):
        self._rootUrl = url
        self._config = {
                            'xpath' : '//div[@class="pages"]/a',
                            'extract_attributes':[{'target_attri_name':'page_count'}] # root url http://www.hhjfsl.com/jfbbs
                        }
            
    def __get_page_count__(self, root):
        items = web_extractor.get_values_from_html_tree(root, self._config)
        if (items is None):
            return 1
         
        page_counts = [Utility.get_value('page_count', provider) for provider in items if provider is not None]
        page_counts = Utility.remove_none_from(page_counts)
         
        page_count = 1
        for item in page_counts:
            current_page_count = int(item)
            if (current_page_count > page_count):
                page_count = current_page_count
        return page_count
    
    def get_page_roots(self):
        root = web_extractor.get_html_root(self._rootUrl)
        page_count = self.__get_page_count__(root)
        page_index = 1
        while page_index <= page_count:
            page_root = root
            if (page_index > 1):
                page_url = self._rootUrl + "&page=" + str(page_index)
                page_root = web_extractor.get_html_root(page_url)
            page_index = page_index + 1
            
            yield page_root
        

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
    def __init__(self, html_root):
        self._root = html_root 
        self._config = {
                    'xpath':'//tr[@class="tr3"]',
                    'extract_attributes':[{'xpath':'./td[2]/a', 'target_attri_name':'title', 'include_text_from_descendant':True},
                                          {'xpath':'./td[2]/a', 'source_attri' : 'href', 'target_attri_name':'source_sub_link'},
                                          {'xpath':'./td[3]/p', 'target_attri_name':'creationTime'},
                                          {'xpath':'./td[3]/a', 'source_attri' : 'href', 'target_attri_name':'author_uid_link'},
                                          {'xpath':'./td[3]/a', 'target_attri_name':'author'},
                                        ]
                }   

    def __convert_time__(self, timeString):
        t = time.strptime(timeString, "%Y-%m-%d")
        converted_time = datetime.datetime(*t[:6])#time.strptime(timeString, "%Y-%m-%d") 
        return converted_time        
           
    def get_summarys(self):
        summarys = web_extractor.get_values_from_html_tree(self._root, self._config)
        if (summarys is None):
            return
        summarys = Utility.remove_none_from(summarys)
        for summary_item in summarys:
            summary_item['creationTime'] = Utility.run_action_when_key_exists('creationTime', summary_item, self.__convert_time__)#self.__convert_time__(summary_item['creationTime'])
        return summarys
    
class DetailProvider:
    def __init__(self, summary):
        self._url = None
        self._summary = summary
        self.__init_detail_url__()
        
        self._config = {'xpath' :'//*[@id="read_tpc"]', 
                        'extract_attributes':[{'target_attri_name':'content', 'include_text_from_descendant' : True}] }
        self._detail = {}
        self._detail[u'author'] = Utility.get_value('author', self._summary)
        self._detail[u'title'] = Utility.get_value('title', self._summary)
        self._detail[u'creationTime'] = Utility.get_value('creationTime', self._summary)
        if self._url:
            self._detail[u'comeFrom'] = {u'category': u'web', u'url': self._url}
        
        
    def __init_detail_url__(self):
        try:
            uid_info = Utility.get_value('author_uid_link', self._summary) #u.php?uid=587
            uid_info = uid_info.replace(u'u.php?', u'')
            if( uid_info.find(u"uid=")< 0):
                return None
                
            detail_url = Utility.get_value('source_sub_link', self._summary) # url like: read.php?tid=18922&fpage=2
            detail_url = re.sub(ur"&fpage=\detail_provider{1,2}", ur"", detail_url) #remove the &gpage=2
        
            #http://www.hhjfsl.com/jfbbs/read.php?tid=18922&uid=587&ds=1&toread=1
            self._url = r'http://www.hhjfsl.com/jfbbs/' + detail_url +'&'+uid_info+'&ds=1&toread=1'
        except Exception,ex:
            print "exception from get_detail_url#", Exception,":",ex
        return None
    
    def get_detail(self):
        if (self._url is None):
            return
        
        root = web_extractor.get_html_root(self._url)
        details = web_extractor.get_values_from_html_tree(root, self._config)
        if (details is None):
            return
        details = Utility.remove_none_from(details)
        if (len(details) != 1):
            print "*error*"
            
        self._detail[u'content'] = Utility.get_value('content', details[0]) 
        return self._detail    
    
class HHJFSLNotesProvider:
    def __init__(self, url):
        self._url = url
        
    def get_all_notes(self):        
        page_provider = PageProvider(self._url)
        for page_root in page_provider.get_page_roots():
            summary_provider = SummaryProvider(page_root)
            items = summary_provider.get_summarys()
            for item in items:
                detail_provider = DetailProvider(item)
                yield detail_provider.get_detail()
    
if __name__ == "__main__":             
    p = HHJFSLNotesProvider("http://www.hhjfsl.com/jfbbs/thread.php?fid=13")
    for note in p.get_all_notes():
        print note
    print "done"