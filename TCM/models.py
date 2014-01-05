# -*- coding: utf-8 -*-
import os, sys
from django.db import models
from django.db.models import Q
import datetime

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

class Book(DataSource):
    def __init__(self, **kwargs):
        DataSource.category = u'Book'
        Model.__init__(self, **kwargs)
        
    title = models.CharField(max_length=255)
    isbn = models.CharField(max_length=255, null = True)
    publishDate = models.DateField(null = True)

class WebInfo(DataSource):
    def __init__(self, **kwargs):
        DataSource.category = u'Web'
        Model.__init__(self, **kwargs)
        
    url = models.URLField(null = False)
         
class ConsiliaSummary(models.Model):    
    author = models.ForeignKey(Person, null = True)
    title = models.CharField(max_length=255, null = True)
    creationTime = models.DateField(null = True)
    description = models.TextField(null=True)
    comeFrom = models.ForeignKey(DataSource, null = True)
    
class ConsiliaDetail(models.Model):
    consilia = models.ForeignKey(ConsiliaSummary)
    index = models.IntegerField()    
    description = models.TextField()
    diagnosis = models.TextField()
    comments = models.TextField() 
    class Meta:
        unique_together = ['consilia', 'index'] # it is better to set primary key, however, it is not supported in django 1.4