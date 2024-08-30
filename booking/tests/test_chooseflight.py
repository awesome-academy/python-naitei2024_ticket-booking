from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import check_password
from django.utils.translation import gettext_lazy as _
from booking.forms import SignUpForm
from booking.constants import STATUS_CHOICES
from booking.models import Flight, FlightTicketType, TicketType, Airport
from django.utils.dateparse import parse_datetime

class ChooseFlightTest(TestCase):
    def setUp(self):
        self.client = Client()
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
            flight_number='A333',
            airline='TestAir',
            departure_airport=self.airport2,
            arrival_airport=self.airport1,
            departure_time=parse_datetime('2069-09-02T15:00:00+0000'),
            arrival_time=parse_datetime('2069-09-02T16:00:00+0000')
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

    def test_get_invalid_number_of_passengers(self):
        response = self.client.get(reverse('index'), {
            'tripType': 'oneway',
            'from': 'HAN',
            'to': 'DAD',
            'departureDate': '2069-09-01',
            'numPassengers': 'one',
            'chairType': 'Economy'
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, _("The number of passengers is not valid."))

    # Ngoại trừ tripType và numPassengers vì 2 trường này có giá trị mặc định
    def test_get_all_the_fields_are_blank(self):
        response = self.client.get(reverse('index'), {
            'tripType': 'round',
            'from': '',
            'to': '',
            'departureDate': '',
            'returnDate': '',
            'numPassengers': '1',
            'chairType': ''
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, _("Fill in all the fields to search for your flights."))
    
    # Chọn đại diện là field fromAirport
    def test_get_a_field_is_blank(self):
        response = self.client.get(reverse('index'), {
            'tripType': 'round',
            'from': '',
            'to': 'DAD',
            'departureDate': '2069-09-01',
            'returnDate': '2069-09-02',
            'numPassengers': '1',
            'chairType': 'Economy'
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, _("Please select a departure airport."))
    
    def test_get_trip_type_is_round_but_blank_return_date(self):
        response = self.client.get(reverse('index'), {
            'tripType': 'round',
            'from': 'HAN',
            'to': 'DAD',
            'departureDate': '2069-09-01',
            'returnDate': '',
            'numPassengers': '1',
            'chairType': 'Economy'
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, _("Please select a return date."))
    
    def test_get_invalid_trip_type(self):
        response = self.client.get(reverse('index'), {
            'tripType': 'twoway',
            'from': 'HAN',
            'to': 'DAD',
            'departureDate': '2069-09-01',
            'returnDate': '2069-09-02',
            'numPassengers': '1',
            'chairType': 'Economy'
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, _("The trip type is not valid."))

    def test_get_invalid_date(self):
        response = self.client.get(reverse('index'), {
            'tripType': 'round',
            'from': 'HAN',
            'to': 'DAD',
            'departureDate': '2069-09-01',
            'returnDate': '20xx-13-ab',
            'numPassengers': '1',
            'chairType': 'Economy'
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, _("The date is not valid."))
    
    def test_get_departure_airport_and_arrival_airport_is_the_same(self):
        response = self.client.get(reverse('index'), {
            'tripType': 'round',
            'from': 'HAN',
            'to': 'HAN',
            'departureDate': '2069-09-01',
            'returnDate': '2069-09-02',
            'numPassengers': '1',
            'chairType': 'Economy'
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, _("Departure and destination airports cannot be the same."))
    
    def test_get_return_date_less_than_departure_date(self):
        response = self.client.get(reverse('index'), {
            'tripType': 'round',
            'from': 'HAN',
            'to': 'DAD',
            'departureDate': '2069-09-01',
            'returnDate': '2069-08-31',
            'numPassengers': '1',
            'chairType': 'Economy'
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, _("Return date cannot be less than departure date."))
    
    def test_get_departure_date_in_the_past(self):
        response = self.client.get(reverse('index'), {
            'tripType': 'round',
            'from': 'HAN',
            'to': 'DAD',
            'departureDate': '2019-08-01',
            'returnDate': '2069-08-31',
            'numPassengers': '1',
            'chairType': 'Economy'
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, _("You cannot book flights from the past."))
    
    def test_get_valid_information_but_find_no_results(self):
        response = self.client.get(reverse('index'), {
            'tripType': 'round',
            'from': 'HAN',
            'to': 'DAD',
            'departureDate': '2069-08-31',
            'returnDate': '2069-09-02',
            'numPassengers': '1',
            'chairType': 'Economy'
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, _("No flights available with the selected criteria. Please try again."))

    def test_get_successful_search_for_oneway_trip(self):
        response = self.client.get(reverse('index'), {
            'tripType': 'oneway',
            'from': 'HAN',
            'to': 'DAD',
            'departureDate': '2069-09-01',
            'numPassengers': '1',
            'chairType': 'Economy'
        })
        self.assertEqual(response.status_code, 200)
        # Có thông tin của flight1, hạng vé Economy
        self.assertContains(response, 'HAN --- DAD')
        self.assertContains(response, '01/09/2069 3:00 PM - 01/09/2069 4:00 PM')
        # Không có thông tin của flight2, hạng vé Economy
        self.assertNotContains(response, 'DAD --- HAN')
        self.assertNotContains(response, '02/09/2069 3:00 PM - 02/09/2069 4:00 PM')

    def test_get_successful_search_for_round_trip(self):
        response = self.client.get(reverse('index'), {
            'tripType': 'round',
            'from': 'HAN',
            'to': 'DAD',
            'departureDate': '2069-09-01',
            'returnDate': '2069-09-02',
            'numPassengers': '1',
            'chairType': 'Economy'
        })
        self.assertEqual(response.status_code, 200)
        # Có thông tin của flight1, hạng vé Economy
        self.assertContains(response, 'HAN --- DAD')
        self.assertContains(response, '01/09/2069 3:00 PM - 01/09/2069 4:00 PM')
        # Có thông tin của flight2, hạng vé Economy
        self.assertContains(response, 'DAD --- HAN')
        self.assertContains(response, '02/09/2069 3:00 PM - 02/09/2069 4:00 PM')
