from django.urls import path
from . import views
from .views import flight_detail, flight_list, pending_cancellations, user_bookings, approve_cancellation, reject_cancellation
urlpatterns = [
    path('', views.index, name='index'),

    path('login', views.login_view, name='login'),
    path('logout', views.logout_view, name='logout'),
    path('register', views.register_view, name='register'),

    path('flight', flight_list, name = 'flight'),
    path('flight/<int:flight_id>/', flight_detail, name='flight_detail'),

    path('book/', user_bookings, name='user_bookings'),
    path('cancelbooking/<int:booking_id>/', views.cancel_booking, name='cancel_booking'),
    
    path('pending-cancellations/', pending_cancellations, name='pending_cancellations'),
    path('approve-cancellation/<int:booking_id>/', approve_cancellation, name='approve_cancellation'),
    path('reject-cancellation/<int:booking_id>/', reject_cancellation, name='reject_cancellation'),
    
    path('review', views.book_infor_view, name='book_infor'),
    path('payment', views.payment_view, name='payment'),
    path('process', views.process_view, name='process'),
    path('flight/ticket/<int:booking_id>', views.print_ticket, name="print_ticket"),

    path('password-reset/', views.password_reset_request, name='password_reset'),
    path('password-reset/done/', views.password_reset_done, name='password_reset_done'),
    path('reset/<uidb64>/<token>/', views.password_reset_confirm, name='password_reset_confirm'),
]
