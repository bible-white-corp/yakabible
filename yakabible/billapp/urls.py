from django.urls import path

from . import views

urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('create/', views.CreateEvView.as_view(), name='create_event'),
    path('connection/', views.ConnectionView.as_view(), name='connection'),
    path('inscription/', views.InscriptionView.as_view(), name='inscription'),
    path('logout/', views.LogOutView, name='log_out'),
    path('event/<int:pk>', views.EventView.as_view(), name='event'),
    path('event/<int:pk>/register', views.RegEventView, name='reg_event'),
    path('events.json', views.EventsJSON, name='events_json')
]
