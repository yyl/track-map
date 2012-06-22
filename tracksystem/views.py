from django.http import HttpResponse
from models import Track
from datetime import datetime
from django.shortcuts import redirect
from annoying.decorators import render_to
from googleplaces import GooglePlaces
import re

# Create your views here.
def query(request):
	latitude_pass = request.GET.get('lat', None)
	longitude_pass = request.GET.get('long', None)	
	if latitude_pass and longitude_pass:
		guess = searchPlaces(latitude_pass, longitude_pass)
		Track(
			time=datetime.now().isoformat(' '), 
			longitude = longitude_pass,
			latitude = latitude_pass,
			place = guess[0],
			plat = guess[1],
			plon = guess[2]
			).save()
	else:
		return redirect('/')

@render_to('map.html')
def map(request):
	points = Track.objects.all()
	# places = searchPlaces(points)
	return {'points': points}
	
## given coordinate, return the name, coordinate of the nearest place
def searchPlaces(latitude, longitude):
	YOUR_API_KEY = 'AIzaSyBN-X539yOgMPKaBMNAMZS2z8iZx0nD-zo'
	categories = []
	for line in open('type.py','r'):
		match = re.search(r"= '(\w+)'", line)
		categories.append(match.group(1))
		
	query_result = GooglePlaces(YOUR_API_KEY).query(
		        lat_lng={u'lat': latitude, u'lng': longitude}, 
				types = mytype,
				rankby='distance')
	result = []
	result.append(query_result.places[0].name)
	result.append(query_result.places[0].geo_location['lat'])
	result.append(query_result.places[0].geo_location['lng'])
	return result
				
		