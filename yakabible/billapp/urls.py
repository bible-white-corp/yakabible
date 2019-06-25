from django.urls import path, include
from django.conf.urls import url
from . import views
from . import views_json

urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('search/', views.search_view, name='search'),

    path('connection/', views.ConnectionView.as_view(), name='connection'),
    path('registration/', views.RegistrationView.as_view(), name='registration'),
    path('registration/after/<int:pk>', views.AfterReg.as_view(), name='after_reg'),
    path('registration/unlock/<int:pk>', views.unlock_user, name="unlock_user"),
    path('logout/', views.LogOutView, name='log_out'),
    path('unsetnotify/', views.NotifyOff, name='notifyoff'),

    path('event/', views.EventsListView.as_view(), name='events_list'),
    path('event/<int:pk>', views.EventView.as_view(), name='event'),
    path('event/<int:pk>/switch_premium', views.switch_premium, name='update_premium'),
    path('event/<int:pk>/edit', views.EventEdit.as_view(), name='edit_event'),
    path('event/<int:pk>/staff', views.EventStaffView.as_view(), name='event_staff'),
    path('event/<int:pk>/register', views.RegEventView, name='reg_event'),
    path('event/<int:pk>/reg_event_success', views.RegEventSuccessView, name='reg_event_success'),
    path('event/<int:pk>/realtime', views.EventRealtime.as_view(), name='event_realtime'),
    path('event/<int:pk>/ask_for_approval', views.ask_approval, name='ask_approval'),
    path('event/to_approve/', views.ApprovingListView.as_view(), name='approving'),
    path('event/<int:pk>/validating/', views.ask_validation, name='validating'),
    path('event/<int:pk>/refusing/', views.ask_refusing, name='refusing'),
    path('event/<int:pk>/staff/<int:user_pk>/association/<int:asso_pk>', views.AddStaffEventView, name='add_staff'),

    path('ticket/<int:pk>', views.TicketDownload, name='ticket'),
    path('ticket/<int:pk>/update', views_json.UpdateTicket, name='ticket_update'),
    path('ticket/<int:pk>/staff_delete', views.DelStaffEventView, name='del_staff'),

    path('assos/', views.AssociationListView.as_view(), name='assos_list'),
    path('assos/<int:pk>', views.AssociationView.as_view(), name='association'),
    path('assos/<int:pk>/delete', views.DeleteAssociation, name='del_asso'),
    path('assos/<int:pk>/dashboard', views.DashboardAssociationView.as_view(), name='dashboard_association'),
    path('assos/<int:pk>/dashboard/update_website', views.update_website, name='update_website'),
    path('assos/<int:pk>/dashboard/add_user', views.AddUserAssosView, name='add_user_assos'),
    path('assos/<int:pk>/dashboard/update_user', views.UpdateUserAssosView, name='update_user_assos'),
    path('assos/<int:pk>/create_event', views.CreateEvView.as_view(), name='create_event'),

    path('events.json', views_json.EventsJSON, name='events_json'),
    path('tickets.json', views_json.TicketsJSON, name='tickets_json'),

    path('profile/', views.Profile_redir, name='own_profile'),
    path('profile/<int:pk>', views.ProfileView.as_view(), name='profile'),

    path('respos/dashboard', views.DashboardRespoView.as_view(), name='dashboard_respo'),

    path('paypal/', include('paypal.standard.ipn.urls')),
    path('payment/<int:pk>/process', views.payment_process, name='paymentProcess'),
    path('payment/done', views.payment_done, name='paymentDone'),
    path('payment/canceled', views.payment_canceled, name='paymentCanceled')
]
