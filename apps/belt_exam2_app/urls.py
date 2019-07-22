from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.register_login),
    url(r'^register$', views.register),
    url(r'^login$', views.login),
    url(r'^dashboard', views.dashboard),
    url(r'^trips/new', views.new_trip),
    url(r'^create_trip', views.create_trip),
    url(r'^delete_trip/(?P<id>\d+)$', views.delete_trip),
    url(r'^trips/edit/(?P<id>\d+)$', views.edit_trip),
    url(r'^edit_process/(?P<id>\d+)$', views.edit_trip_process),
    url(r'^join_trip/(?P<id>\d+)$', views.join_trip),
    url(r'^unjoin_trip/(?P<id>\d+)$', views.unjoin_trip),
    url(r'^trips/(?P<id>\d+)$', views.trip_info)
]
