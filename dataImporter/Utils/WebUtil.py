# -*- coding: utf-8 -*-
import sys
import os
import re
import time
from lxml import etree
from StringIO import StringIO
from urllib2 import urlopen

reload(sys)
#sys.setdefaultencoding('utf-8')
sys.path.append(os.path.dirname(__file__))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__),"..")))

from Utility import *
  
class web_extractor(object):
    def get_content_from(url):
        tried_time = 0
        waited_time = 1
        while tried_time < 10:
            try:
                print "loading data from: " + url
                item = urlopen(url)
                content = item.read()
                item.close()
                return Utility.escape(content)
            except Exception,ex:
                print "exception from get_content_from#", Exception,":",ex
                tried_time += 1
                waited_time = waited_time * 2
                time.sleep( waited_time )    
    get_content_from = staticmethod(get_content_from)
    
    def get_end_text(tag):
        blocks = ['address', 'blockquote', 'body', 'br', 'dd', 'dir', 'div', 'dl', 'dt', 'fieldset', 'form', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'hr', 'html', 'legend', 'menu', 'ol', 'p', 'ul'] 
        none_display = ['head', 'input', 'link', 'meta', 'script', 'style', 'title'] 
        inline_elements = ['a', 'abbr', 'acronym', 'b', 'big',  'cite', 'code', 'del', 'dfn', 'em', 'font', 'i', 'ins', 'kbd', 'label', 'option', 'q', 'samp', 'small', 'strike', 'strong', 'sub', 'sup', 'tt', 'u', 'var']
        list_item = ['li']
        inline_block = ['button', 'input', 'select', 'textarea']
        table = ['table']
        table_caption = ['caption'] 
        table_row_group = ['tbody']
        table_row = ['tr']
        table_cell = ['td', 'th'] 
        
        end_text_category = {'\n':[], ' ':[], '':[]}
        end_text_category['\n'].extend(blocks)
        end_text_category['\n'].extend(list_item)
        end_text_category['\n'].extend(none_display)
        end_text_category['\n'].extend(inline_block)
        end_text_category['\n'].extend(table)
        end_text_category['\n'].extend(table_caption)
        end_text_category['\n'].extend(table_row_group)
        end_text_category['\n'].extend(table_row)
        
        end_text_category[' '].extend(inline_elements)
        end_text_category[' '].extend(table_cell)
       
        prefix = ' '
        postfix = ' '
        for key, value in end_text_category.items():
            if tag in value:
                if tag=='br':
                    prefix = key
                else:
                    postfix = key                   
                return prefix, postfix

        return ' ', ' '
    get_end_text = staticmethod(get_end_text)

    def get_full_text(element):
        prefix, postfix = web_extractor.get_end_text(element.tag)            
        items = [element.prefix, element.text, element.tail]
        text = prefix + ''.join([item for item in items if item is not None]).strip() + postfix
        #print "element.tag:"+ element.tag + " text:" + text
        return text
    
    get_full_text = staticmethod(get_full_text)
        
    def get_text(element, include_text_from_descendant):
        if (not include_text_from_descendant):
            return element.text
        #return ''.join([web_extractor.get_full_text(descendant) for descendant in element.iter()])
        full_text = ''
        for child in element.iter():
            full_text += web_extractor.get_full_text(child)
        return full_text
        #return etree.tostring(element)
    
    get_text = staticmethod(get_text)            

    def extract_single_attribute(element, attri_info):
        source_attri_name = Utility.get_value('source_attri', attri_info)
        target_attri_name = Utility.get_value('target_attri_name', attri_info, source_attri_name)
        
        if (target_attri_name is None):
            return None
        
        attribute_value = None
        if (source_attri_name is not None):            
            attribute_value = element.get(source_attri_name)
        else:
            include_text_from_descendant = Utility.get_bool_value('include_text_from_descendant', attri_info)
            attribute_value = web_extractor.get_text(element, include_text_from_descendant)
                
        if (target_attri_name is None or attribute_value is None):
            return None
        
        #print attribute_value
        return {target_attri_name : attribute_value}
        
    extract_single_attribute = staticmethod(extract_single_attribute)    
        
    def extract_attributes(element, attributes):
        attribute_values = {}
        for attri_info in attributes:
            from_element = element
            xpath_value = Utility.get_value('xpath', attri_info)
            if (xpath_value is not None):
                children = element.xpath(xpath_value)    
                if children is None or len(children) != 1:
                    continue    
                from_element = children[0]

            single_value = web_extractor.extract_single_attribute(from_element, attri_info)    
            if (single_value is not None):
                attribute_values.update(single_value)
                
        return attribute_values

    extract_attributes = staticmethod(extract_attributes)    
    
    def extract_children(element, children_config):
        if (children_config is None or element is None):
            return None
            
        all_properties = []
        for prop in children_config:
            item = web_extractor.get_values_from_html_tree(element, prop)
            Utility.append_if_not_none(item, all_properties)
        
        if len(all_properties) > 0:
            return all_properties
        return None
        
    extract_children = staticmethod(extract_children)
    
    def get_values_from_html_tree(root, config):
        try:            
            xpath_name = 'xpath'
            if (xpath_name in config):
                root = root.xpath(config[xpath_name])        
            
            children_key = 'children' 
            children_config = Utility.get_value(children_key, config)
            all_values = []
            for element in root:
                value_item = {}
                children_value = web_extractor.extract_children(element, children_config)
                Utility.update_dictionary_if_not_none(children_key, children_value, value_item)
                
                attributes_key = 'extract_attributes'
                if (attributes_key in config):
                    attributes_value = web_extractor.extract_attributes(element, config[attributes_key])
                    #Utility.update_dictionary_if_not_none(attributes_key, attributes_value, value_item)
                Utility.append_if_not_none(attributes_value, all_values)    
                #all_values.append(value_item)
                
            if len(all_values) > 0:
                return all_values
        except Exception,ex:
            print Exception,":",ex
        
        return None
            
    get_values_from_html_tree = staticmethod(get_values_from_html_tree)
    
    def get_html_root_from_content(content):
        parser = etree.HTMLParser()
        html_tree = etree.parse(StringIO(content), parser)
        root = html_tree.getroot()
        return root
    
    get_html_root_from_content = staticmethod(get_html_root_from_content)        
    
    def get_html_root(url):
        content = web_extractor.get_content_from(url)
        return web_extractor.get_html_root_from_content(content)
    
    get_html_root = staticmethod(get_html_root)        
        
    def get_values_from_url(url, config):
        root = web_extractor.get_html_root(url)
        items = web_extractor.get_values_from_html_tree(root, config)
        return items 
           
    get_values_from_url = staticmethod(get_values_from_url)    