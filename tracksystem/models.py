from django.db import models

# Create your models here.
class Track(models.Model):
	time = models.DateTimeField('time')
	latitude = models.FloatField()
	longitude = models.FloatField()
	place = models.CharField(max_length=100, default='place')
	plat = models.FloatField(default = 30.45)
	plon = models.FloatField(default=104.6)