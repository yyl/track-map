from django.http import HttpResponse
from models import Track, Place
from datetime import datetime
from django.shortcuts import redirect
from annoying.decorators import render_to
from googleplaces import GooglePlaces
import re, os
import urllib2, urllib
from django.views.decorators.csrf import csrf_exempt

SITE_ROOT = os.path.dirname(os.path.realpath(__file__))

@csrf_exempt
def query(request):
	if request.method == 'POST':
		latitude_pass = request.POST.get('lat', None)
		longitude_pass = request.POST.get('long', None)	
	else:
		latitude_pass = request.GET.get('lat', None)
		longitude_pass = request.GET.get('long', None)	
		
	if latitude_pass and longitude_pass:
		# guess[0] = place name, guess[1] = place lat, guess[2] = place longitude
		guess = searchPlaces(latitude_pass, longitude_pass)
		if guess[0] not in Place.objects.all():
			predict = Place(name=guess[0], latitude=guess[1], longitude=guess[2])
			predict.save()
		else:
			predict = Place.objects.get(name=guess[0])
		Track(
			latitude = latitude_pass,
			longitude = longitude_pass,
			prediction=predict
			).save()
		return HttpResponse('GET successful')
	else:
		return redirect('/')

def delete(request, id):
	emp = Track.objects.get(pk = id)
	emp.delete()
	return redirect('/')

def deleteall(request):
	Track.objects.all().delete()
	return redirect('/')

# def test(request):
# 	guess = searchPlaces(40.5213555, -74.4562968)
# 	Track(
# 		time=datetime.now().isoformat(' '), 
# 		latitude = 40.5213555,
# 		longitude = -74.4562968,
# 		place = guess[0],
# 		plat = guess[1],
# 		plon = guess[2]
# 		).save()
# 	return redirect('/')
		
## given coordinate, return the name, coordinate of the nearest place
def searchPlaces(latitude, longitude):
	YOUR_API_KEY = 'AIzaSyBN-X539yOgMPKaBMNAMZS2z8iZx0nD-zo'
	categories = []
	result = []
	for line in open(os.path.join(SITE_ROOT, 'type.py'),'r'):
		match = re.search(r"= '(\w+)'", line)
		categories.append(match.group(1))
	
	if categories != []:
		query_result = GooglePlaces(YOUR_API_KEY).query(
		        lat_lng={u'lat': latitude, u'lng': longitude}, 
				types = categories,
				rankby='distance')
	else:
		result = [1,404,1]
	if query_result.places != []:
		result.append(query_result.places[0].name)
		result.append(query_result.places[0].geo_location['lat'])
		result.append(query_result.places[0].geo_location['lng'])
	else:
		result = [3,404,2]
	return result
				
		