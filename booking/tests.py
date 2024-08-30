from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from booking.models import Flight, Airport, Booking, FlightTicketType, TicketType
from django.contrib.messages import get_messages
from django.utils.translation import activate
from django.utils import timezone

class FlightDetailViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.departure_airport = Airport.objects.create(
            airport_code="JFK", name="John F. Kennedy", city="New York", country="USA"
        )
        self.arrival_airport = Airport.objects.create(
            airport_code="LAX", name="Los Angeles International", city="Los Angeles", country="USA"
        )
        self.flight = Flight.objects.create(
            flight_number="AA100", 
            airline="American Airlines", 
            departure_airport=self.departure_airport, 
            arrival_airport=self.arrival_airport,
            departure_time="2024-08-30 08:00:00",
            arrival_time="2024-08-30 11:00:00"
        )

    def test_flight_detail_view(self):
        url = reverse('flight_detail', args=[self.flight.flight_id])
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'flight_detail.html')
        self.assertEqual(response.context['flight'], self.flight)
        self.assertEqual(response.context['departure_airport'], self.departure_airport)
        self.assertEqual(response.context['arrival_airport'], self.arrival_airport)

class FlightListViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.departure_airport = Airport.objects.create(
            airport_code="JFK", name="John F. Kennedy", city="New York", country="USA"
        )
        self.arrival_airport = Airport.objects.create(
            airport_code="LAX", name="Los Angeles International", city="Los Angeles", country="USA"
        )
        self.flight1 = Flight.objects.create(
            flight_number="AA100", 
            airline="American Airlines", 
            departure_airport=self.departure_airport, 
            arrival_airport=self.arrival_airport,
            departure_time="2024-08-30 08:00:00",
            arrival_time="2024-08-30 11:00:00"
        )
        self.flight2 = Flight.objects.create(
            flight_number="AA101", 
            airline="American Airlines", 
            departure_airport=self.departure_airport, 
            arrival_airport=self.arrival_airport,
            departure_time="2024-09-01 08:00:00",
            arrival_time="2024-09-01 11:00:00"
        )

    def test_flight_list_view(self):
        url = reverse('flight')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'flight_list.html')
        self.assertEqual(list(response.context['flights']), [self.flight1, self.flight2])

    def test_flight_list_view_with_filters(self):
        url = reverse('flight')
        response = self.client.get(url, {'departure_date': '2024-08-30'})
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(list(response.context['flights']), [self.flight1])
        
        response = self.client.get(url, {'departure_location': 'New York'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(list(response.context['flights']), [self.flight1, self.flight2])
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.contrib.messages import get_messages
from booking.models import Account, FlightTicketType, Flight, Booking

User = get_user_model()

class BookingTests(TestCase):
    
    def setUp(self):
        activate('en')
        # Create Airport instances
        self.departure_airport = Airport.objects.create(
            airport_code="DPT", 
            name="Departure Airport", 
            city="Test City", 
            country="Test Country"
        )
        self.arrival_airport = Airport.objects.create(
            airport_code="ARR", 
            name="Arrival Airport", 
            city="Test City", 
            country="Test Country"
        )
        
        # Create User and Admin instances
        self.user = Account.objects.create_user(
            username='testuser', 
            password='12345', 
            email='testuser@example.com'
        )
        self.admin_user = Account.objects.create_superuser(
            username='admin', 
            password='adminpass', 
            email='admin@example.com'
        )
        
        # Create Flight instance
        self.flight = Flight.objects.create(
            flight_number="FL123",
            airline="Test Airline",
            departure_airport=self.departure_airport, 
            arrival_airport=self.arrival_airport, 
            departure_time=timezone.now(), 
            arrival_time=timezone.now() + timezone.timedelta(hours=2)
        )
        
        self.ticket_type = TicketType.objects.create(
            name="Normal"
        )

        # Create FlightTicketType instance
        self.flight_ticket_type = FlightTicketType.objects.create(
            flight=self.flight, 
            ticket_type=self.ticket_type, 
            price=100, 
            available_seats=10
        )
        
        # Create Booking instance
        self.booking = Booking.objects.create(
            account=self.user, 
            flight_ticket_type=self.flight_ticket_type, 
            seat_number="12A", 
            status="Confirmed"
        )

    def test_user_bookings_view(self):
        self.client.login(username='testuser', password='12345')
        response = self.client.get(reverse('user_bookings'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'user_bookings.html')
        self.assertContains(response, self.ticket_type.name)

    def test_cancel_booking_view(self):
        self.client.login(username='testuser', password='12345')
        response = self.client.post(reverse('cancel_booking', args=[self.booking.booking_id]))
        self.booking.refresh_from_db()
        self.assertEqual(self.booking.status, 'PendingCancellation')
        self.assertRedirects(response, reverse('user_bookings'))
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(str(messages[0]), "Your booking cancellation request has been submitted and is pending approval.")

    def test_cancel_booking_view_not_owner(self):
        other_user = Account.objects.create_user(username='otheruser', password='12345', email='otheruser@example.com')
        self.client.login(username='otheruser', password='12345')
        response = self.client.post(reverse('cancel_booking', args=[self.booking.booking_id]))
        self.assertRedirects(response, reverse('user_bookings'))
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(str(messages[0]), "You do not have permission to cancel this booking.")

    def test_pending_cancellations_view(self):
        self.client.login(username='admin', password='adminpass')
        self.booking.set_status('PendingCancellation')
        self.booking.save()
        response = self.client.get(reverse('pending_cancellations'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'pending_cancellations.html')
        self.assertContains(response, self.ticket_type.name)

    def test_approve_cancellation_view(self):
        self.client.login(username='admin', password='adminpass')
        self.booking.set_status('PendingCancellation')
        self.booking.save()
        response = self.client.post(reverse('approve_cancellation', args=[self.booking.booking_id]))
        self.booking.refresh_from_db()
        self.assertEqual(self.booking.status, 'Canceled')
        self.assertRedirects(response, reverse('pending_cancellations'))
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(str(messages[0]), "Cancellation approved successfully.")

    def test_reject_cancellation_view(self):
        self.client.login(username='admin', password='adminpass')
        self.booking.set_status('PendingCancellation')
        self.booking.save()
        response = self.client.post(reverse('reject_cancellation', args=[self.booking.booking_id]))
        self.booking.refresh_from_db()
        self.assertEqual(self.booking.status, 'DeniedCancellation')
        self.assertRedirects(response, reverse('pending_cancellations'))
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(str(messages[0]), "Cancellation rejected.")


