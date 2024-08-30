from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import check_password
from django.utils.translation import gettext_lazy as _
from booking.forms import SignUpForm
from booking.constants import STATUS_CHOICES
from booking.models import Account, Flight, FlightTicketType, TicketType, Airport
from django.utils.dateparse import parse_datetime

class BookInforTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = Account.objects.create_user(
            email="tester@example.com",
            username="tester",
            password="12345678",
            phone_number="0123456789"
        )
        self.tickettype1 = TicketType.objects.create(name="Economy")
        self.airport1 = Airport.objects.create(
            airport_code='HAN',
            name='Noi Bai International Airport',
            city='Ha Noi',
            country='Viet Nam'
        )
        self.airport2 = Airport.objects.create(
            airport_code='DAD',
            name='Da Nang International Airport',
            city='Da Nang',
            country='Viet Nam'
        )
        self.flight1 = Flight.objects.create(
            flight_number='A333',
            airline='TestAir',
            departure_airport=self.airport1,
            arrival_airport=self.airport2,
            departure_time=parse_datetime('2069-09-01T15:00:00+0000'),
            arrival_time=parse_datetime('2069-09-01T16:00:00+0000')
        )
        self.flight2 = Flight.objects.create(
            flight_number='A334',
            airline='TestAir2',
            departure_airport=self.airport2,
            arrival_airport=self.airport1,
            departure_time=parse_datetime('2069-09-02T15:00:00+0000'),
            arrival_time=parse_datetime('2069-09-02T16:00:00+0000')
        )
        self.flight3 = Flight.objects.create(
            flight_number='A335',
            airline='TestAir3',
            departure_airport=self.airport1,
            arrival_airport=self.airport2,
            departure_time=parse_datetime('2069-09-02T15:00:00+0000'),
            arrival_time=parse_datetime('2069-09-02T16:00:00+0000')
        )
        self.flight4 = Flight.objects.create(
            flight_number='A336',
            airline='TestAir4',
            departure_airport=self.airport2,
            arrival_airport=self.airport1,
            departure_time=parse_datetime('2069-09-01T15:00:00+0000'),
            arrival_time=parse_datetime('2069-09-01T16:00:00+0000')
        )
        self.flight5 = Flight.objects.create(
            flight_number='A337',
            airline='TestAir5',
            departure_airport=self.airport1,
            arrival_airport=self.airport2,
            departure_time=parse_datetime('2020-09-01T15:00:00+0000'),
            arrival_time=parse_datetime('2020-09-01T16:00:00+0000')
        )
        self.flighttickettype1 = FlightTicketType.objects.create(
            flight=self.flight1,
            ticket_type=self.tickettype1,
            price=1200000,
            available_seats=20,
        )
        self.flighttickettype2 = FlightTicketType.objects.create(
            flight=self.flight2,
            ticket_type=self.tickettype1,
            price=1200000,
            available_seats=20,
        )
        self.flighttickettype3 = FlightTicketType.objects.create(
            flight=self.flight3,
            ticket_type=self.tickettype1,
            price=1200000,
            available_seats=20,
        )
        self.flighttickettype4 = FlightTicketType.objects.create(
            flight=self.flight4,
            ticket_type=self.tickettype1,
            price=1200000,
            available_seats=20,
        )
        self.flighttickettype5 = FlightTicketType.objects.create(
            flight=self.flight5,
            ticket_type=self.tickettype1,
            price=1200000,
            available_seats=20,
        )
    
    def test_get_book_infor_user_not_authenticated(self):
        response = self.client.get(reverse('book_infor'), {
            'd_flight_id': self.flight1.flight_id,
            'r_flight_id': self.flight2.flight_id,
            'flight_ticket_type': 'Economy',
            'num_passengers': '1'
        })
        self.assertEqual(response.status_code, 302)
        self.assertIn('/booking/login', response.url)

    def test_get_book_infor_information_is_not_enough(self):
        login = self.client.login(username='tester', password='12345678')
        self.assertEqual(login, True)
        response = self.client.get(reverse('book_infor'), {
            'd_flight_id': self.flight1.flight_id,
            'r_flight_id': self.flight2.flight_id,
            'flight_ticket_type': 'Economy',
        })
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('index'))
        messages = list(response.wsgi_request._messages)
        self.assertEqual(len(messages), 1)
        self.assertEqual(messages[0].message, _("Too few information."))

    # Flight id phải là các số tự nhiên
    def test_get_book_infor_invalid_flight_id(self):
        login = self.client.login(username='tester', password='12345678')
        self.assertEqual(login, True)
        response = self.client.get(reverse('book_infor'), {
            'd_flight_id': 'a',
            'r_flight_id': self.flight2.flight_id,
            'flight_ticket_type': 'Economy',
            'num_passengers': '1'
        })
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('index'))
        messages = list(response.wsgi_request._messages)
        self.assertEqual(len(messages), 1)
        self.assertEqual(messages[0].message, _("Flight ID is not valid."))


    def test_get_book_infor_invalid_num_passengers(self):
        login = self.client.login(username='tester', password='12345678')
        self.assertEqual(login, True)
        response = self.client.get(reverse('book_infor'), {
            'd_flight_id': self.flight1.flight_id,
            'r_flight_id': self.flight2.flight_id,
            'flight_ticket_type': 'Economy',
            'num_passengers': 'ab'
        })
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('index'))
        messages = list(response.wsgi_request._messages)
        self.assertEqual(len(messages), 1)
        self.assertEqual(messages[0].message, _("Invalid number of passengers."))


    def test_get_book_infor_num_passengers_too_large(self):
        login = self.client.login(username='tester', password='12345678')
        self.assertEqual(login, True)
        response = self.client.get(reverse('book_infor'), {
            'd_flight_id': self.flight1.flight_id,
            'r_flight_id': self.flight2.flight_id,
            'flight_ticket_type': 'Economy',
            'num_passengers': '21'
        })
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('index'))
        messages = list(response.wsgi_request._messages)
        self.assertEqual(len(messages), 1)
        self.assertEqual(messages[0].message, _("Number of passengers is too large."))

    
    def test_get_book_infor_invalid_ticket_type(self):
        login = self.client.login(username='tester', password='12345678')
        self.assertEqual(login, True)
        response = self.client.get(reverse('book_infor'), {
            'd_flight_id': self.flight1.flight_id,
            'r_flight_id': self.flight2.flight_id,
            'flight_ticket_type': 'Ecofriendly',
            'num_passengers': '1'
        })
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('index'))
        messages = list(response.wsgi_request._messages)
        self.assertEqual(len(messages), 1)
        self.assertEqual(messages[0].message, _("Seat type is not valid."))

    
    # Flight 5 là một chuyến bay trong quá khứ.
    def test_get_book_infor_book_for_past_flight(self):
        login = self.client.login(username='tester', password='12345678')
        self.assertEqual(login, True)
        response = self.client.get(reverse('book_infor'), {
            'd_flight_id': self.flight5.flight_id,
            'r_flight_id': self.flight2.flight_id,
            'flight_ticket_type': 'Economy',
            'num_passengers': '1'
        })
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('index'))
        messages = list(response.wsgi_request._messages)
        self.assertEqual(len(messages), 1)
        self.assertEqual(messages[0].message, _("You cannot book flight from the past."))


    # Khi chuyến bay về (flight 3) có điểm đi khác điểm đến của chuyến bay đi (flight 1)
    # và điểm đi của chuyến bay đi (flight 1) khác so với điểm đến của chuyến bay về (flight 3)
    def test_get_book_infor_airport_between_flights_mismatch(self):
        login = self.client.login(username='tester', password='12345678')
        self.assertEqual(login, True)
        response = self.client.get(reverse('book_infor'), {
            'd_flight_id': self.flight1.flight_id,
            'r_flight_id': self.flight3.flight_id,
            'flight_ticket_type': 'Economy',
            'num_passengers': '1'
        })
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('index'))
        messages = list(response.wsgi_request._messages)
        self.assertEqual(len(messages), 1)
        self.assertEqual(messages[0].message, _("Airports are mismatch."))


    # Flight 4 có thời gian sớm hơn (hoặc cùng lúc) với flight 1
    def test_get_book_infor_return_flight_sooner_than_departure_flight(self):
        login = self.client.login(username='tester', password='12345678')
        self.assertEqual(login, True)
        response = self.client.get(reverse('book_infor'), {
            'd_flight_id': self.flight1.flight_id,
            'r_flight_id': self.flight4.flight_id,
            'flight_ticket_type': 'Economy',
            'num_passengers': '1'
        })
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('index'))
        messages = list(response.wsgi_request._messages)
        self.assertEqual(len(messages), 1)
        self.assertEqual(messages[0].message, _("Return flight is sooner than departure flight."))
    
    # Dành cho vé 1 chiều (oneway)
    def test_get_book_infor_successful_for_one_flight(self):
        login = self.client.login(username='tester', password='12345678')
        self.assertEqual(login, True)
        response = self.client.get(reverse('book_infor'), {
            'd_flight_id': self.flight1.flight_id,
            'flight_ticket_type': 'Economy',
            'num_passengers': '1'
        })
        self.assertEqual(response.status_code, 200)
        # Chứa thông tin flight 1
        self.assertContains(response, 'A333')
        self.assertContains(response, 'TestAir')
        # Không chứa thông tin các chuyến bay khác
        self.assertNotContains(response, 'A334')
        self.assertNotContains(response, 'TestAir2')
        self.assertNotContains(response, 'A335')
        self.assertNotContains(response, 'TestAir3')
        self.assertNotContains(response, 'A336')
        self.assertNotContains(response, 'TestAir4')
        self.assertNotContains(response, 'A337')
        self.assertNotContains(response, 'TestAir5')

    # Dành cho vé khứ hồi (round)
    def test_get_book_infor_successful_for_round_trip(self):
        login = self.client.login(username='tester', password='12345678')
        self.assertEqual(login, True)
        response = self.client.get(reverse('book_infor'), {
            'd_flight_id': self.flight1.flight_id,
            'r_flight_id': self.flight2.flight_id,
            'flight_ticket_type': 'Economy',
            'num_passengers': '1'
        })
        self.assertEqual(response.status_code, 200)
        # Chứa thông tin flight 1
        self.assertContains(response, 'A333')
        self.assertContains(response, 'TestAir')
        # Chứa thông tin flight 2
        self.assertContains(response, 'A334')
        self.assertContains(response, 'TestAir2')
        # Không chứa các chuyến bay còn lại
        self.assertNotContains(response, 'A335')
        self.assertNotContains(response, 'TestAir3')
        self.assertNotContains(response, 'A336')
        self.assertNotContains(response, 'TestAir4')
        self.assertNotContains(response, 'A337')
        self.assertNotContains(response, 'TestAir5')
