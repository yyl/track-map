from django.http import HttpResponse
from models import Track
from datetime import datetime
from django.shortcuts import redirect
from annoying.decorators import render_to

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
	return {'points': points}