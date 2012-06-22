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
		guess = searchPlaces(40.5213555, -74.4562968)
		Track(
			time=datetime.now().isoformat(' '), 
			longitude = longitude_pass,
			latitude = latitude_pass,
			# place = guess[0],
			# plat = guess[1],
			# plon = guess[2]
			).save()
	else:
		return redirect('/')

def delete(request, id):
	emp = Track.objects.get(pk = id)
	emp.delete()
	return redirect('/')

def deleteall(request):
	Track.objects.all().delete()
	return redirect('/')
	
## given coordinate, return the name, coordinate of the nearest place
def searchPlaces(latitude, longitude):
	YOUR_API_KEY = 'AIzaSyBN-X539yOgMPKaBMNAMZS2z8iZx0nD-zo'
	categories = []
	for line in open('type.py','r'):
		match = re.search(r"= '(\w+)'", line)
		categories.append(match.group(1))
	
	if categories != []:
		query_result = GooglePlaces(YOUR_API_KEY).query(
		        lat_lng={u'lat': latitude, u'lng': longitude}, 
				types = categories,
				rankby='distance')
	else:
		result = [1,2,3]
	result = []
	result.append(query_result.places[0].name)
	result.append(query_result.places[0].geo_location['lat'])
	result.append(query_result.places[0].geo_location['lng'])
	return result
				
		