from django.db import models
from datetime import datetime

# Create your models here.
class Place(models.Model):
	time = models.DateTimeField('time')
	name = models.CharField(max_length=100, default='N/A')
	latitude = models.FloatField()
	longitude = models.FloatField()
	
	def __unicode__(self):
		return u"%s: (%f, %f)" % (self.name, self.latitude, self.longitude)
	

class Track(models.Model):
	time = models.DateTimeField('time')
	latitude = models.FloatField()
	longitude = models.FloatField()
	prediction = models.ForeignKey(Place, default=1)
	
	def __unicode__(self):
		return u"(%f, %f)" % (self.latitude, self.longitude)
