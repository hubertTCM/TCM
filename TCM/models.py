# -*- coding: utf-8 -*-
import datetime
import os
import sys

from django.db import models
from django.db.models import Q

"""TCM = Traditional Chinese Medical"""
class Person(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(null=True)
  
SOURCE_CATEGORY = (
    (u'Original', u'原创'),
    (u'Web', u'网络'),
    (u'Book', u'书刊'),
)  

class DataSource(models.Model):
    category = models.CharField(max_length=30, choices=SOURCE_CATEGORY)
    
DISEASE_CATEGORY = (
    (u'TCM', u'中医'),
    (u'Modern', u'西医')
                    )
class Disease(models.Model):
    name = models.CharField(max_length = 50, primary_key=True)
    category = models.CharField(max_length=20, choices = DISEASE_CATEGORY)

# do not rewrite __init___ in model class, otherwise, exception happens
class Book(DataSource):  
    title = models.CharField(max_length=255)
    isbn = models.CharField(max_length=255, null = True)
    publishDate = models.DateField(null = True)

class WebInfo(DataSource):        
    url = models.URLField(null = False)
    
class MedicalNote(models.Model):  
    author = models.ForeignKey(Person)
    title = models.CharField(max_length=255)
    content = models.TextField(null=True)
    creationTime = models.DateField(null = True)
    comeFrom = models.ForeignKey(DataSource, null = True)
    
    def json(self):
        json_object = {}
        json_object[u'id'] = self.id
        json_object[u'author'] = self.author.name
        json_object[u'title'] = self.title
        json_object[u'content'] = self.content
         
        if (self.creationTime != None):
            json_object[u'creationTime'] = str(self.creationTime)          
        if (self.comeFrom):
            json_object[u'source'] = self.comeFrom.category
            json_object[u'source_id'] = self.comeFrom.id
        return json_object
         
class ConsiliaSummary(models.Model):    
    author = models.ForeignKey(Person, null = True)
    title = models.CharField(max_length=255, null = True)
    creationTime = models.DateField(null = True)
    description = models.TextField(null=True)
    comeFrom = models.ForeignKey(DataSource, null = True)
    
    def json(self):
        json_object = {}
        json_object[u'id'] = self.id
        json_object[u'author'] = self.author.name
        json_object[u'title'] = self.title
        if (self.creationTime != None):
            json_object[u'creationTime'] = str(self.creationTime)
        if (self.description):
            json_object[u'description'] = self.description            
        if (self.comeFrom):
            json_object[u'source'] = self.comeFrom.category
            json_object[u'source_id'] = self.comeFrom.id
        return json_object
    
class ConsiliaDetail(models.Model):
    consilia = models.ForeignKey(ConsiliaSummary)
    index = models.IntegerField()    
    description = models.TextField(null = True)
    diagnosis = models.TextField()
    comments = models.TextField(null = True) 
    
    def json(self):
        json_object = {'id' : self.id, 'consilia_id' : self.consilia.id, 'index' : self.index, 'diagnosis' : self.diagnosis}
        if (self.description != None):
            json_object['description'] = self.description
        if (self.comments != None):
            json_object['comments'] = self.comments        
        return json_object
    
    class Meta:
        unique_together = ['consilia', 'index'] # it is better to set primary key, however, it is not supported in django 1.4
                
class ConsiliaDiseaseConnection(models.Model):
    consilia = models.ForeignKey(ConsiliaSummary)
    disease = models.ForeignKey(Disease)
    class Meta:
        unique_together = ['consilia', 'disease']
        
class Clause(models.Model): 
    index = models.IntegerField(null = False)
    content = models.TextField(null = False)
    comeFrom = models.ForeignKey(Book, null = False)
        