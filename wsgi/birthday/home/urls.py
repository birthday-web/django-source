from django.conf.urls import patterns, include, url
from . import views
urlpatterns = [ 
	url(r'^$', views.index),
	url(r'^posts/(?P<username>\w{1,50})/$', views.listPosts),
	url(r'^posts/(?P<username>\w{1,50})/delcmt/(?P<comment_id>\d){1,10}/$', views.delComment),
	url(r'^posts/(?P<username>\w{1,50})/delpost/(?P<post_id>\d{1,10})/$', views.delPost),
]
