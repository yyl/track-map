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

SITE_ROOT = os.path.dirname(os.path.realpath(__file__))

class UploadForm(forms.Form):
	file = forms.FileField()

def map(request):
	# from_zone = tz.tzutc()
	# to_zone = tz.tzlocal()
	# 
	# utc_times = [obj.time.replace(tzinfo=from_zone) for obj.time in Track.objecs.all()]
	# local_times = [time.astimezone(to_zone) for time in utc_times]
	# 
	# Convert time zone
	# central = utc.astimezone(to_zone)
	return render_to_response(
			'track_list.html', 
			{'object_list': Track.objects.all(),}, 
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

# file format: 2012-07-07 16:00, (40.5543564, -70.5787453), ...
def handle_file_upload(f):
	output = False
	for line in f.readlines():
		matchtime = re.search(r'([-:\d\s]+),', line)
		match1= re.search(r'\(([-\.\d]+),', line)
		match2 = re.search(r', ([-\.\d]+)\),', line)
		if match1 and match2 and matchtime:
			time = datetime.strptime(matchtime.group(1), "%Y-%m-%d %H:%M")
			longitude = float(match1.group(1))
			latitude = float(match2.group(1))
			# guess[0] = place name, guess[1] = place lat, guess[2] = place longitude
			guess = searchPlaces(latitude, longitude)
			places = [obj.name for obj in Place.objects.all()]
			if guess[0] not in places:
				predict = Place(name=guess[0], latitude=guess[1], longitude=guess[2], time=time)
				predict.save()
			else:
				predict = Place.objects.get(name=guess[0])
			Track(
				latitude = latitude,
				longitude = longitude,
				prediction=predict,
				time=time
				).save()
			output = True
	return output
	
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

