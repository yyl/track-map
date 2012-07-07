from django.contrib.admin import site
from tracksystem.models import Track, Place

site.register(Track)
site.register(Place)