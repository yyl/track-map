from django.conf.urls import patterns, include, url
from django.contrib import admin
from tracksystem.models import Track

admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
	url(r'^$', 'tracksystem.views.map'),
	url(r'^query$', 'tracksystem.views.query'),
	url(r'^delete/(\d+)$', 'tracksystem.views.delete'),
	url(r'^delete_all$', 'tracksystem.views.deleteall'),
	url(r'^upload$', 'tracksystem.views.upload'),
    # url(r'^myheroku/', include('myheroku.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
)
