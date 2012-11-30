from django.http import HttpResponse
from models import Track, Place
from django.shortcuts import redirect, render_to_response
from googleplaces import GooglePlaces
import re, os, math
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
	right = Place.objects.filter(right=True)
	left = Place.objects.filter(right=False)
	return render_to_response(
				'track_list.html', 
				{'object_list': Track.objects.order_by('-time'),
				# 'place_list': unknown,
				'evens': right,
				'odds': left
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
	# Place.objects.all().delete()	
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
	
# classify current places into 2 sides
def side(request):	
	right = Place.objects.filter(right=True)
	return render_to_response(
				'track_list.html', 
				{'object_list': Track.objects.all(),
				'evens': right
				}, 
				RequestContext(request)
			)

def deviation(request):
	return render_to_response(
				'deviation.html', 
				{'object_list': Track.objects.order_by('-time'),
				}, 
				RequestContext(request)
			)
							
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
		match3 = re.search(r'A:([\d.]+)', line)
		if match1 and match2 and matchtime:
			lat = float(match2.group(1))
			lon = float(match1.group(1))
			accu = float(match3.group(1))
			if Track.objects.count() == 0 or distance(lat, lon, Track.objects.latest('time')) > 23:
				time = datetime.strptime(matchtime.group(1), "%Y-%m-%d-%H-%M-%S")
				longitude = lon
				latitude = lat
				Track(
					latitude = latitude,
					longitude = longitude,
					accu = accu,
					time=time
					).save()
				output = True

	placesOnPath(Track.objects.all())
	return output

# return True if the point (lat, lon) is 10+ meters away from the track point
def distance(lat, lon, track):
	degrees_to_radians = math.pi/180.0
	
	# phi = 90 - latitude
	phi1 = (90.0 - lat)*degrees_to_radians
	phi2 = (90.0 - float(track.latitude))*degrees_to_radians

	# theta = longitude
	theta1 = lon*degrees_to_radians
	theta2 = float(track.longitude)*degrees_to_radians
	
	cos = (math.sin(phi1)*math.sin(phi2)*math.cos(theta1 - theta2) + 
	       math.cos(phi1)*math.cos(phi2))
	arc = math.acos(cos)
	
	return arc*6371*1000
	
## given coordinates, do a google place search, return top 20 places matches the search
def googlePlaces(lat, lon):
	YOUR_API_KEY = 'AIzaSyBN-X539yOgMPKaBMNAMZS2z8iZx0nD-zo'
	try:
		qresult = GooglePlaces(YOUR_API_KEY).query(
	        lat_lng={u'lat': lat, u'lng': lon}, 
			types=TYPES,
			radius=40)
		return qresult.places
	except:
		render_to_response(
					'apierror.html', 
					{}
		)
	
# given a path, represented as a sequence of coordinates, search all nearby places 
# path format: [(lat1, lon1), (lat2, lon2),....]
def placesOnPath(path):
	count = 0
	for point in path:
		pointplaces = googlePlaces(point.latitude, point.longitude)
		for place in pointplaces:
			place.get_details()
			if not existing(Place.objects.all(), place) and hasRoute(place):
				now = datetime.utcnow().replace(tzinfo=tz.tzutc())
				predict = Place(name=place.name, 
								latitude=place.geo_location['lat'], 
								longitude=place.geo_location['lng'], 
								address=place.formatted_address,
								point=point,
								time=now)
				if count == 0:
					predict.right = isRightSide(point, path[count+1], predict)
				else:
					predict.right = isRightSide(path[count-1], point, predict)
				predict.save()	
		count += 1
	
# check if a place is already in the place list
def existing(places, new):
	names = [place.name for place in places]
	addresses = [place.address for place in places]
	return new.name in names or new.formatted_address in addresses
	
# return True if the place has a street address
# place is the GooglePlace class in google places api
def hasRoute(place):
	for dic in place.details[u'address_components']:
	      if dic[u'types'] == [u'route']:
	        return True
	else:
		return False

# return true if the place is on the right side of the road
def isRightSide(point1, point2, place):
	lat1 = point1.latitude
	lon1 = point1.longitude
	lat2 = point2.latitude
	lon2 = point2.longitude
	lat3 = place.latitude
	lon3 = place.longitude	
	return (lat2 - lat1) * (lon3 - lon1) - (lon2 - lon1) * (lat3 - lat1) > 0