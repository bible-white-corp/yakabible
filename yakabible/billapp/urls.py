from django.urls import path

from . import views
from . import views_json

urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('create/', views.CreateEvView.as_view(), name='create_event'),
    path('connection/', views.ConnectionView.as_view(), name='connection'),
    path('registration/', views.RegistrationView.as_view(), name='registration'),
    path('logout/', views.LogOutView, name='log_out'),
    path('event/<int:pk>', views.EventView.as_view(), name='event'),
    path('event/<int:pk>/register', views.RegEventView, name='reg_event'),
    path('event/<int:pk>/reg_event_success', views.RegEventSuccessView, name='reg_event_success'),
    path('assos/<int:pk>', views.AssociationView.as_view(), name='association'),
    path('events.json', views_json.EventsJSON, name='events_json'),
    path('tickets.json', views_json.TicketsJSON, name='tickets_json'),
    path('assos/', views.AssociationListView.as_view(), name='assos_list')
]
