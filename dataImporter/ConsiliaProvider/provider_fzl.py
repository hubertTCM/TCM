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
	parent = os.path.dirname(__file__)
	for i in range(levels):
		sys.path.append(parent)
		parent = os.path.abspath(os.path.join(parent, ".."))
		
appendAncestorsToSystemPath(3)

from dataImporter.Utils.Utility import *

class Provider_fzl:	
	def __exact_detail_situation(self, sourceText, targetDictionary):
		diagnosis_keywords =[u'处方：', u'处方一：', u'处方: ']
		index = -1
		for keyword in diagnosis_keywords:
			index = sourceText.find(keyword)
			if(index >= 0):
				targetDictionary['description'] = sourceText[:index]
				targetDictionary['diagnosis'] = sourceText[index:]
				print 'description:  ' + targetDictionary['description']
				print 'diagnosis:  ' + targetDictionary['diagnosis']
				break
		
		if (index < 0):
			targetDictionary['diagnosis'] = sourceText
			print 'diagnosis:  ' + targetDictionary['diagnosis']
			
	def __exact_detail(self, whichTime, sourceText):
		comment_keywords = (u'［按语］', u'［辨证］')
		detail = {}
		for keyword in comment_keywords:
			index = sourceText.find(keyword)
			if(index >= 0):
				self.__exact_detail_situation(sourceText[:index], detail)
				detail['comments'] = sourceText[index:]
				print 'comment:  ' + detail['comments']				
				return detail
			
		self.__exact_detail_situation(sourceText, detail)		
		return detail
		
	def _createAllDetails(self, which_time, sourceText, targetDetails):
		index = sourceText.find(u'诊］', 3)
		if (index > 0):
			self.__exact_detail(which_time, sourceText[:index - 2].strip())
			self._createAllDetails(which_time + 1, sourceText[index - 2:].strip(), targetDetails)
		else:
			detailItem = self.__exact_detail(which_time, sourceText)
			targetDetails.append((which_time, detailItem))
	
	def __createConsilia(self, title, content):
		content = content[content.index(title) + len(title):].strip()
		keywords = (u'［初诊］', u'［一诊］', u'［诊治］')
		
		consilia = {}
	
		for keyword in keywords:
			index = content.find(keyword)
			if(index >= 0):
				consilia['description'] = content[:index]
				content = content[index:]
				print 'description:  ' + consilia['description'] 				
				break

		details = []
		self._createAllDetails(1, content.strip(), details)
		consilia['details'] = details
		return consilia
	
	def _exactTitleInformation(self, sourceText):
		pass
	def getAllConsilias(self):			
		file = codecs.open('fzl.txt', 'r', 'utf-8', 'ignore')
		content = file.read()
		file.close()
	
		matches = re.findall(ur"(\d{1,2}\u3001.+)", content, re.M)
		for i in range(len(matches)):
			itemstart = matches[i]
			if i == len(matches) - 1:
				'''last sourceText'''
				sourceText = content[content.index(itemstart):]
			else:
				sourceText = content[content.index(itemstart):content.index(matches[i+1])]
			sourceText = sourceText.strip()
			#print itemstart
			#return
			index = itemstart.find(u'、') + 1
			title = itemstart[index:]
			#title = itemstart.split(u'、')[1].strip()
			print title	
			consilia = {'comeFrom': {'category': u'Book', 'Name': u'范中林六经辨证医案'}, 'Author': u'范中林'}	
			self._exactTitleInformation(title)		
			Utility.update_dict(consilia, self.__createConsilia(title, sourceText))
			#yield consilia			

p = Provider_fzl()
p.getAllConsilias()

