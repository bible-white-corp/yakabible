from django.urls import path

from . import views

urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('create/', views.CreateEvView.as_view(), name='create_event'),
    path('connection/', views.ConnectionView.as_view(), name='connection'),
    path('events.json', views.EventsJSON, name='events_json')
]
