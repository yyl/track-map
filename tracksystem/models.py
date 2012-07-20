from django.db import models
from datetime import datetime
import re

# Create your models here.
class Place(models.Model):
	time = models.DateTimeField('time')
	name = models.CharField(max_length=100, default='N/A')
	address = models.CharField(max_length=300, default='N/A', unique=True)
	latitude = models.FloatField()
	longitude = models.FloatField()
	
	def __unicode__(self):
		return u"%s: (%f, %f) [%s]" % (self.name, self.latitude, self.longitude, self.address)
	
	# return the street number of this place
	def streetNumber(self):
		street_number = re.search(r'\d+', self.address)
		if street_number:
			return street_number.group()
		else:
			return "N/A"

class Track(models.Model):
	time = models.DateTimeField('time')
	latitude = models.FloatField()
	longitude = models.FloatField()
	
	
	def __unicode__(self):
		return u"(%f, %f)" % (self.latitude, self.longitude)
