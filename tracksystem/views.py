from django.http import HttpResponse
from models import Track
from datetime import datetime

# Create your views here.
def query(request):
	latitude_pass = request.GET.get('lat', None)
	longitude_pass = request.GET.get('long', None)	
	if latitude_pass and longitude_pass:
		point = Track(
					time=datetime.now().isoformat(' '), 
					longitude = longitude_pass,
					latitude = latitude_pass)
		point.save()
		return HttpResponse("Hello, world! "+ point.longitude)
	else:
		return HttpResponse("Parameters are not in a correct form.")