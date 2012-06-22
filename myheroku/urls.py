from django.conf.urls import patterns, include, url
from django.contrib import admin
from tracksystem.models import Track

admin.autodiscover()

post_dict = {
	'queryset': Track.objects.all().order_by('time'),
}

urlpatterns = patterns('',
    # Examples:
	(r'^$', 'django.views.generic.list_detail.object_list', post_dict),
	url(r'^query$', 'tracksystem.views.query'),
	url(r'^delete/(\d+)$', 'tracksystem.views.delete'),
	url(r'^delete_all$', 'tracksystem.views.deleteall'),
    # url(r'^myheroku/', include('myheroku.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
)
