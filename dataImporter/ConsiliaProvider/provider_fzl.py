# -*- coding: utf-8 -*-
import sys
import os
import time
import codecs
import re
from urllib import urlopen
from django.core.management import setup_environ

reload(sys)
sys.setdefaultencoding('utf-8')

def appendAncestorsToSystemPath(levels):
	parentFolder = os.path.dirname(__file__)
	for i in range(levels):
		sys.path.append(parentFolder)
		parentFolder = os.path.abspath(os.path.join(parentFolder,".."))
		
appendAncestorsToSystemPath(3)

from dataImporter.Utils.Utility import *

class Provider_fzl:
	def __createConsilias(self, content):
		pass
	
	def getAllConsilias(self):			
		file = codecs.open('fzl.txt', 'r', 'utf-8', 'ignore')
		content = file.read()
		file.close()
	
		matches = re.findall(ur"(\d{1,2}\u3001.+)", content, re.M)
		for i in range(len(matches)):
			itemstart = matches[i]
			if i == len(matches) - 1:
				'''last item'''
				item = content[content.index(itemstart):]
			else:
				item = content[content.index(itemstart):content.index(matches[i+1])]
			item = item.strip()
			#print itemstart
			#return
			index = itemstart.find(u'、') + 1
			title = itemstart[index:]
			#title = itemstart.split(u'、')[1].strip()
			print title	
			consilia = {'comeFrom': {'category': u'Book', 'Name': u'范中林六经辨证医案'}, 'Author': u'范中林'}
			
			

p = Provider_fzl()
p.getAllConsilias()


def exact_detail_situation(detail, item):
	diagnosis_keywords =[u'处方：', u'处方一：', u'处方: ']
	index = -1
	for keyword in diagnosis_keywords:
		index = item.find(keyword)
		if(index >= 0):
			detail.description = item[:index]
			detail.diagnosis = item[index:]
			break
	
	if (index < 0):
		detail.diagnosis = item

def exact_detail(summary, which_time, item):
	comment_keywords = (u'［按语］', u'［辨证］')
	detail = YiAnDetail()
	detail.index = which_time
	detail.yian = summary
	
	for keyword in comment_keywords:
		index = item.find(keyword)
		if(index >= 0):
			exact_detail_situation(detail, item[:index])
			detail.comments = item[index:]
			
			print detail.description
			print "***"
			print detail.diagnosis
			print "***"
			print detail.comments
			print "###"
			
			detail.save()
			return
	
	exact_detail_situation(detail, item)
	detail.save()
	print detail.description
	print "***"
	print detail.diagnosis
	print "###"
	
def exact_detail_list(summary, which_time, item):
	index = item.find(u'诊］', 3)
	if (index > 0):
		exact_detail(summary, which_time, item[:index - 2].strip())
		exact_detail_list(summary, which_time + 1, item[index - 2:].strip())
	else:
		exact_detail(summary, which_time, item)

def exact(doctor, title, item):
	summary = YiAnSummary()
	summary.author = doctor
	summary.title = title

	item = item[item.index(title) + len(title):].strip()
	keywords = (u'［初诊］', u'［一诊］', u'［诊治］')

	for keyword in keywords:
		index = item.find(keyword)
		if(index >= 0):
			summary.description = item[:index]
			item = item[index:]
			break
	print summary.description
	print "***"
	summary.sourceCategory = u'Book'
	summary.sourceDetail = u'范中林六经辨证医案'
	summary.save()
	return exact_detail_list(summary, 1, item.strip())
	
	tlist = item.split(u'［')
	
"""
	tlist = item.split(u'［')
	if tlist[2].find(u'此') > 0:
		temp_index = tlist[2].index(u'此')
		split_index = len(tlist[0]) + len(tlist[1]) + temp_index + 2
	elif tlist[2].find(u'证') > 0:
		temp_index = tlist[2].index(u'证')
		split_index = len(tlist[0]) + len(tlist[1]) + temp_index + 2
	else:
		temp_index = tlist[1].index(u'此')
		split_index = len(tlist[0]) + temp_index + 1
	situation = item[item.index(title) + len(title):split_index]
	diagnosis = item[split_index:]	
"""

def import_fzl():
	doctor, is_created = TCMDoctor.objects.get_or_create(name=u'范中林')
	if (is_created):
		doctor.save()
		
	file = codecs.open('fzl.txt', 'r', 'gbk', 'ignore')
	content = file.read()
	file.close()

	matches = re.findall(ur"(\d{1,2}\u3001.+)", content, re.M)
	for i in range(len(matches)):
		itemstart = matches[i]
		if i == len(matches) - 1:
			'''last item'''
			item = content[content.index(itemstart):]
		else:
			item = content[content.index(itemstart):content.index(matches[i+1])]
		item = item.strip()
		#print itemstart
		#return
		index = itemstart.find(u'、') + 1
		title = itemstart[index:]
		#title = itemstart.split(u'、')[1].strip()
		print title
		print '############'		
		exact(doctor, title, item)
