from django.http import HttpResponse
from models import Track, Place
from django.shortcuts import redirect, render_to_response
from googleplaces import GooglePlaces
import re, os
from datetime import datetime
from dateutil import tz
from django.views.decorators.csrf import csrf_exempt
from django import forms
from django.template import RequestContext

# preprocessing
####################
# current file path
SITE_ROOT = os.path.dirname(os.path.realpath(__file__))
# all possible types of places, read from type.py file
TYPES = []
for line in open(os.path.join(SITE_ROOT, 'type.py'),'r'):
	match = re.search(r"= '(\w+)'", line)
	TYPES.append(match.group(1))
####################

class UploadForm(forms.Form):
	file = forms.FileField()

# draw the map based on Track table
# display tracks and nearby places
def map(request):
	return render_to_response(
				'track_list.html', 
				{'object_list': Track.objects.all(),
				'place_list': Place.objects.all()
				}, 
				RequestContext(request)
			)
	
@csrf_exempt
def query(request):
	if request.method == 'POST':
		latitude_pass = request.POST.get('lat', None)
		longitude_pass = request.POST.get('long', None)	
	else:
		latitude_pass = request.GET.get('lat', None)
		longitude_pass = request.GET.get('long', None)	
		
	if latitude_pass and longitude_pass:
		now = datetime.utcnow().replace(tzinfo=tz.tzutc())
		# guess[0] = place name, guess[1] = place lat, guess[2] = place longitude
		guess = searchPlaces(latitude_pass, longitude_pass)
		places = [obj.name for obj in Place.objects.all()]
		# use it from db if already exist, otherwise create a new one
		if guess[0] not in places:
			predict = Place(name=guess[0], latitude=guess[1], longitude=guess[2], time=now)
			predict.save()
		else:
			predict = Place.objects.get(name=guess[0])
		Track(
			latitude = latitude_pass,
			longitude = longitude_pass,
			prediction=predict,
			time=now
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
	Place.objects.all().delete()	
	return redirect('/')


def upload(request):
	if request.method == 'POST': # If the form has been submitted...
		form = UploadForm(request.POST, request.FILES) # A form bound to the POST data
		if form.is_valid(): # All validation rules pass
			# Process the data in form.cleaned_data
			# ...
			output = handle_file_upload(request.FILES['file']) 
			if output == True:
				return redirect("/")
			else:
				return HttpResponse("""<p>Invalid file format; correct format:</p>
										<p>2012-07-07 16:00, (40.5543564, -70.5787453), ...</p>
										<a href='/upload'>Back to upload</a>""",  RequestContext(request))
	else:
		form = UploadForm() # An unbound form

	return render_to_response('upload.html', {'form': form,}, RequestContext(request))
	
########################
# helper method	
########################

# extract time, loatitude, longitude info from the file and put them into database
# file format: 2012-07-07 16:00, (40.5543564, -70.5787453), ...
def handle_file_upload(f):
	output = False
	for line in f.readlines():
		matchtime = re.search(r'time: ([\d\s:-]+)', line)
		match1= re.search(r'longitude: ([\d\s\.-]+)', line)
		match2 = re.search(r'latitude: ([\d\s\.-]+)', line)
		if match1 and match2 and matchtime:
			time = datetime.strptime(matchtime.group(1), "%Y-%m-%d-%H-%M-%S")
			longitude = float(match1.group(1))
			latitude = float(match2.group(1))
			Track(
				latitude = latitude,
				longitude = longitude,
				time=time
				).save()
			output = True
	path = trackToPath()
	if path != False:
		placesOnPath(path)
	return output

## given coordinates, do a google place search, return top 20 places matches the search
def googlePlaces(lat, lon):
	YOUR_API_KEY = 'AIzaSyBN-X539yOgMPKaBMNAMZS2z8iZx0nD-zo'
	qresult = GooglePlaces(YOUR_API_KEY).query(
	        lat_lng={u'lat': lat, u'lng': lon}, 
			types=TYPES,
			radius=30)
			
	return qresult.places
		
## given coordinate, return the name, coordinate of the nearest place
def searchPlaces(latitude, longitude):
	places = googlePlaces(latitude, longitude)
	
	if places != []:
		result.append(query_result.places[0].name)
		result.append(query_result.places[0].geo_location['lat'])
		result.append(query_result.places[0].geo_location['lng'])
	else:
		result = [3,404,2]
	return result

# extract the path from the Track model
def trackToPath():
	if Track.objects.all() != []:
		return [(track.latitude, track.longitude) for track in Track.objects.all()]	
	else:
		return False
	
# given a path, represented as a sequence of coordinates, search all nearby places 
# path format: [(lat1, lon1), (lat2, lon2),....]
def placesOnPath(path):
	for point in path:
		pointplaces = googlePlaces(point[0], point[1])
		for place in pointplaces:
			if not existing(Place.objects.all(), place):
				now = datetime.utcnow().replace(tzinfo=tz.tzutc())
				predict = Place(name=place.name, 
								latitude=place.geo_location['lat'], 
								longitude=place.geo_location['lng'], 
								time=now)
				predict.save()	
	
# check if a place is already in the place list
def existing(places, new):
	names = [place.name for place in places]
	return new.name in names