from django.http import HttpResponse
from models import Track
from datetime import datetime
from django.shortcuts import redirect
from annoying.decorators import render_to
# from googleplaces import GooglePlaces
# import re

# Create your views here.
def query(request):
	latitude_pass = request.GET.get('lat', None)
	longitude_pass = request.GET.get('long', None)	
	if latitude_pass and longitude_pass:
		Track(
			time=datetime.now().isoformat(' '), 
			longitude = longitude_pass,
			latitude = latitude_pass
			).save()
	else:
		return redirect('/')

@render_to('map.html')
def map(request):
	points = Track.objects.all()
	# places = searchPlaces(points)
	return {'points': points}
	
# 
# def searchPlaces(points):
# 	YOUR_API_KEY = 'AIzaSyBN-X539yOgMPKaBMNAMZS2z8iZx0nD-zo'
# 	categories = []
# 	for line in open('type.py','r'):
# 		match = re.search(r"= '(\w+)'", line)
# 		categories.append(match.group(1))
# 		
# 	for point in points:
# 		query_result = GooglePlaces(YOUR_API_KEY).query(
# 		        lat_lng={u'lat': point.latitude, u'lng': point.longitude}, 
# 				types = mytype,
# 				rankby='distance')
				
		