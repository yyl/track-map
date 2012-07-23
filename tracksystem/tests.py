"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from django.test import TestCase
from models import Track, Place
from datetime import datetime
from views import farEnough

class HelperTest(TestCase):
	def setUp(self):
		self.t1 = Track.objects.create(latitude=40.500379, longitude=-74.425107,
					time=datetime.now())  
		self.t2 = Track.objects.create(latitude=40.50039, longitude=-74.425024,
					time=datetime.now())
		
	def test_far_enough(self):
		self.assertTrue(farEnough(float(self.t1.latitude), float(self.t1.longitude), self.t2))