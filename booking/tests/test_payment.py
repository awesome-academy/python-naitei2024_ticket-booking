from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import check_password
from django.utils.translation import gettext_lazy as _
from booking.forms import SignUpForm
from booking.constants import STATUS_CHOICES, BOOKING_STATUS
from booking.models import Account, Flight, FlightTicketType, TicketType, Airport, Booking
from django.utils.dateparse import parse_datetime

class PaymentTest(TestCase):
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
        self.airport3 = Airport.objects.create(
            airport_code='NRT',
            name='Narita International Airport',
            city='Tokyo',
            country='Japan'
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
        self.flight6 = Flight.objects.create(
            flight_number='A338',
            airline='TestAir6',
            departure_airport=self.airport1,
            arrival_airport=self.airport3,
            departure_time=parse_datetime('2069-09-01T15:00:00+0000'),
            arrival_time=parse_datetime('2069-09-01T16:00:00+0000')
        )
        self.flight7 = Flight.objects.create(
            flight_number='A339',
            airline='TestAir7',
            departure_airport=self.airport3,
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
        self.flighttickettype6 = FlightTicketType.objects.create(
            flight=self.flight6,
            ticket_type=self.tickettype1,
            price=5000000,
            available_seats=20,
        )
        self.flighttickettype7 = FlightTicketType.objects.create(
            flight=self.flight7,
            ticket_type=self.tickettype1,
            price=5000000,
            available_seats=20,
        )
        self.context = {
            'flight1': self.flight1.flight_id,
            'flight1Class': 'Economy',
            'flight2': self.flight2.flight_id,
            'flight2Class': 'Economy',
            'countryCode': '84',
            'mobile': '0123456888',
            'email': 'tester@gmail.com',
            'numPassengers': '1',
            'passenger0Fname': 'New',
            'passenger0Lname': 'Tester',
            'passenger0Gender': 'Male',
            'passenger0DateOfBirth': '2003-10-16',
            'passenger0Nationality': 'Viet Nam'
        }
    
    def test_post_payment_user_not_authenticated(self):
        response = self.client.post(reverse('payment'), self.context)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/booking/login?next=/booking/payment')
    
    def test_post_payment_countrycode_is_missing(self):
        login = self.client.login(username="tester", password="12345678")
        self.assertTrue(login)
        self.context["countryCode"] = ""
        response = self.client.post(reverse('payment'), self.context)
        self.assertEqual(response.status_code, 302)
        messages = list(response.wsgi_request._messages)
        self.assertEqual(messages[0].message, _("Please select a country code."))
        
    def test_post_payment_phone_number_is_missing(self):
        login = self.client.login(username="tester", password="12345678")
        self.assertTrue(login)
        self.context["mobile"] = ""
        response = self.client.post(reverse('payment'), self.context)
        self.assertEqual(response.status_code, 302)
        messages = list(response.wsgi_request._messages)
        self.assertEqual(messages[0].message, _("Please input your phone number."))

    def test_post_payment_phone_number_is_invalid(self):
        login = self.client.login(username="tester", password="12345678")
        self.assertTrue(login)
        self.context["mobile"] = "abcxyz&85*"
        response = self.client.post(reverse('payment'), self.context)
        self.assertEqual(response.status_code, 302)
        messages = list(response.wsgi_request._messages)
        self.assertEqual(messages[0].message, _("Your phone number is not valid."))
    
    def test_post_payment_email_is_missing(self):
        login = self.client.login(username="tester", password="12345678")
        self.assertTrue(login)
        self.context["email"] = ""
        response = self.client.post(reverse('payment'), self.context)
        self.assertEqual(response.status_code, 302)
        messages = list(response.wsgi_request._messages)
        self.assertEqual(messages[0].message, _("Please input your email."))

    def test_post_payment_email_is_invalid(self):
        login = self.client.login(username="tester", password="12345678")
        self.assertTrue(login)
        self.context["email"] = "123@569**"
        response = self.client.post(reverse('payment'), self.context)
        self.assertEqual(response.status_code, 302)
        messages = list(response.wsgi_request._messages)
        self.assertEqual(messages[0].message, _("Your email is not valid."))

    def test_post_payment_flight_id_is_missing(self):
        login = self.client.login(username="tester", password="12345678")
        self.assertTrue(login)
        self.context["flight1"] = ""
        response = self.client.post(reverse('payment'), self.context)
        self.assertEqual(response.status_code, 302)
        messages = list(response.wsgi_request._messages)
        self.assertEqual(messages[0].message, _("The departure flight is not valid."))

    def test_post_payment_flight_id_is_invalid(self):
        login = self.client.login(username="tester", password="12345678")
        self.assertTrue(login)
        self.context["flight1"] = "abc"
        response = self.client.post(reverse('payment'), self.context)
        self.assertEqual(response.status_code, 302)
        messages = list(response.wsgi_request._messages)
        self.assertEqual(messages[0].message, _("The departure flight is not valid."))

    def test_post_payment_flight_is_in_the_past(self):
        login = self.client.login(username="tester", password="12345678")
        self.assertTrue(login)
        self.context["flight1"] = self.flight5.flight_id
        response = self.client.post(reverse('payment'), self.context)
        self.assertEqual(response.status_code, 302)
        messages = list(response.wsgi_request._messages)
        self.assertEqual(messages[0].message, _("The departure flight is not valid."))

    # Khi chuyến bay về (flight 3) có điểm đi khác điểm đến của chuyến bay đi (flight 1)
    # và điểm đi của chuyến bay đi (flight 1) khác so với điểm đến của chuyến bay về (flight 3)
    def test_post_payment_return_flight_airports_and_departure_flight_airports_mismatch(self):
        login = self.client.login(username="tester", password="12345678")
        self.assertTrue(login)
        self.context["flight1"] = self.flight1.flight_id
        self.context["flight2"] = self.flight3.flight_id
        response = self.client.post(reverse('payment'), self.context)
        self.assertEqual(response.status_code, 302)
        messages = list(response.wsgi_request._messages)
        self.assertEqual(messages[0].message, _("The return flight is not valid."))

    # Flight 4 có thời gian sớm hơn (hoặc cùng lúc) với flight 1
    def test_post_payment_return_flight_sooner_than_departure_flight(self):
        login = self.client.login(username='tester', password='12345678')
        self.assertEqual(login, True)
        self.context["flight1"] = self.flight1.flight_id
        self.context["flight2"] = self.flight4.flight_id
        response = self.client.post(reverse('payment'), self.context)
        self.assertEqual(response.status_code, 302)
        messages = list(response.wsgi_request._messages)
        self.assertEqual(messages[0].message, _("The return flight is not valid."))

    def test_post_payment_num_passengers_is_missing(self):
        login = self.client.login(username='tester', password='12345678')
        self.assertEqual(login, True)
        self.context["numPassengers"] = ""
        response = self.client.post(reverse('payment'), self.context)
        self.assertEqual(response.status_code, 302)
        messages = list(response.wsgi_request._messages)
        self.assertEqual(messages[0].message, _("Your information is not valid. Please try again."))
    
    def test_post_payment_num_passengers_is_invalid(self):
        login = self.client.login(username='tester', password='12345678')
        self.assertEqual(login, True)
        self.context["numPassengers"] = "abc"
        response = self.client.post(reverse('payment'), self.context)
        self.assertEqual(response.status_code, 302)
        messages = list(response.wsgi_request._messages)
        self.assertEqual(messages[0].message, _("Your information is not valid. Please try again."))

    def test_post_payment_passenger_first_name_is_missing(self):
        login = self.client.login(username='tester', password='12345678')
        self.assertEqual(login, True)
        self.context["passenger0Fname"] = ""
        response = self.client.post(reverse('payment'), self.context)
        self.assertEqual(response.status_code, 302)
        messages = list(response.wsgi_request._messages)
        self.assertEqual(messages[0].message, _("Please input the first names."))

    # Tên riêng không hợp lệ khi chứa các ký tự đặc biệt và số
    def test_post_payment_passenger_first_name_is_invalid(self):
        login = self.client.login(username='tester', password='12345678')
        self.assertEqual(login, True)
        self.context["passenger0Fname"] = "ab3&*"
        response = self.client.post(reverse('payment'), self.context)
        self.assertEqual(response.status_code, 302)
        messages = list(response.wsgi_request._messages)
        self.assertEqual(messages[0].message, _("Some of the first names are not valid."))

    def test_post_payment_passenger_last_name_is_missing(self):
        login = self.client.login(username='tester', password='12345678')
        self.assertEqual(login, True)
        self.context["passenger0Lname"] = ""
        response = self.client.post(reverse('payment'), self.context)
        self.assertEqual(response.status_code, 302)
        messages = list(response.wsgi_request._messages)
        self.assertEqual(messages[0].message, _("Please input the last names."))

    # Tên riêng không hợp lệ khi chứa các ký tự đặc biệt và số
    def test_post_payment_passenger_last_name_is_invalid(self):
        login = self.client.login(username='tester', password='12345678')
        self.assertEqual(login, True)
        self.context["passenger0Lname"] = "ab3&*"
        response = self.client.post(reverse('payment'), self.context)
        self.assertEqual(response.status_code, 302)
        messages = list(response.wsgi_request._messages)
        self.assertEqual(messages[0].message, _("Some of the last names are not valid."))

    def test_post_payment_passenger_gender_is_missing(self):
        login = self.client.login(username='tester', password='12345678')
        self.assertEqual(login, True)
        self.context["passenger0Gender"] = ""
        response = self.client.post(reverse('payment'), self.context)
        self.assertEqual(response.status_code, 302)
        messages = list(response.wsgi_request._messages)
        self.assertEqual(messages[0].message, _("Please select the genders."))

    # Giới tính chỉ có: Male, Female hoặc Other
    def test_post_payment_passenger_gender_is_invalid(self):
        login = self.client.login(username='tester', password='12345678')
        self.assertEqual(login, True)
        self.context["passenger0Gender"] = "Gay"
        response = self.client.post(reverse('payment'), self.context)
        self.assertEqual(response.status_code, 302)
        messages = list(response.wsgi_request._messages)
        self.assertEqual(messages[0].message, _("Some of the genders are not valid."))

    def test_post_payment_passenger_date_of_birth_is_missing(self):
        login = self.client.login(username='tester', password='12345678')
        self.assertEqual(login, True)
        self.context["passenger0DateOfBirth"] = ""
        response = self.client.post(reverse('payment'), self.context)
        self.assertEqual(response.status_code, 302)
        messages = list(response.wsgi_request._messages)
        self.assertEqual(messages[0].message, _("Please input the dates of birth."))
    
    def test_post_payment_passenger_date_of_birth_is_invalid(self):
        login = self.client.login(username='tester', password='12345678')
        self.assertEqual(login, True)
        self.context["passenger0DateOfBirth"] = "20xx-xx?22"
        response = self.client.post(reverse('payment'), self.context)
        self.assertEqual(response.status_code, 302)
        messages = list(response.wsgi_request._messages)
        self.assertEqual(messages[0].message, _("Some of the dates of birth are not valid."))

    def test_post_payment_passenger_date_of_birth_is_greater_than_now(self):
        login = self.client.login(username='tester', password='12345678')
        self.assertEqual(login, True)
        self.context["passenger0DateOfBirth"] = "2069-01-01"
        response = self.client.post(reverse('payment'), self.context)
        self.assertEqual(response.status_code, 302)
        messages = list(response.wsgi_request._messages)
        self.assertEqual(messages[0].message, _("The dates of birth should be prior to today."))

    # Một số test case tiếp theo kiểm tra trong trường hợp là chuyến bay ra nước ngoài
    # (Sẽ có thêm các trường như: số hộ chiếu, nơi cấp, ngày hết hạn, v.v.)
    def test_post_payment_passenger_passport_number_is_missing(self):
        login = self.client.login(username='tester', password='12345678')
        self.assertEqual(login, True)
        self.context["flight1"] = self.flight6.flight_id
        self.context["flight2"] = self.flight7.flight_id
        self.context["passenger0PassportNumber"] = ""
        self.context["passenger0CountryOfIssue"] = "Vietnam"
        self.context["passenger0PassportExpireDate"] = "2070-01-01"
        response = self.client.post(reverse('payment'), self.context)
        self.assertEqual(response.status_code, 302)
        messages = list(response.wsgi_request._messages)
        self.assertEqual(messages[0].message, _("Please input the passport numbers."))

    # Chứa các ký tự đặc biệt thì sẽ không hợp lệ
    def test_post_payment_passenger_passport_number_is_invalid(self):
        login = self.client.login(username='tester', password='12345678')
        self.assertEqual(login, True)
        self.context["flight1"] = self.flight6.flight_id
        self.context["flight2"] = self.flight7.flight_id
        self.context["passenger0PassportNumber"] = "N@#***123"
        self.context["passenger0CountryOfIssue"] = "Vietnam"
        self.context["passenger0PassportExpireDate"] = "2070-01-01"
        response = self.client.post(reverse('payment'), self.context)
        self.assertEqual(response.status_code, 302)
        messages = list(response.wsgi_request._messages)
        self.assertEqual(messages[0].message, _("Some of the passport numbers are not valid."))

    def test_post_payment_passenger_expire_date_is_missing(self):
        login = self.client.login(username='tester', password='12345678')
        self.assertEqual(login, True)
        self.context["flight1"] = self.flight6.flight_id
        self.context["flight2"] = self.flight7.flight_id
        self.context["passenger0PassportNumber"] = "N12345678"
        self.context["passenger0CountryOfIssue"] = "Vietnam"
        self.context["passenger0PassportExpireDate"] = ""
        response = self.client.post(reverse('payment'), self.context)
        self.assertEqual(response.status_code, 302)
        messages = list(response.wsgi_request._messages)
        self.assertEqual(messages[0].message, _("Please input the passport expire dates."))

    def test_post_payment_passenger_expiry_date_is_invalid(self):
        login = self.client.login(username='tester', password='12345678')
        self.assertEqual(login, True)
        self.context["flight1"] = self.flight6.flight_id
        self.context["flight2"] = self.flight7.flight_id
        self.context["passenger0PassportNumber"] = "N12345678"
        self.context["passenger0CountryOfIssue"] = "Vietnam"
        self.context["passenger0PassportExpireDate"] = "207x-13-xx"
        response = self.client.post(reverse('payment'), self.context)
        self.assertEqual(response.status_code, 302)
        messages = list(response.wsgi_request._messages)
        self.assertEqual(messages[0].message, _("Some of the expire dates are not valid."))

    def test_post_payment_passenger_expiry_date_is_sooner_than_now(self):
        login = self.client.login(username='tester', password='12345678')
        self.assertEqual(login, True)
        self.context["flight1"] = self.flight6.flight_id
        self.context["flight2"] = self.flight7.flight_id
        self.context["passenger0PassportNumber"] = "N12345678"
        self.context["passenger0CountryOfIssue"] = "Vietnam"
        self.context["passenger0PassportExpireDate"] = "2020-01-01"
        response = self.client.post(reverse('payment'), self.context)
        self.assertEqual(response.status_code, 302)
        messages = list(response.wsgi_request._messages)
        self.assertEqual(messages[0].message, _("Some of the passports are not usable anymore."))
    
    # Dữ liệu context ban đầu là hợp lệ.
    def test_post_payment_all_the_fields_are_valid(self):
        login = self.client.login(username='tester', password='12345678')
        self.assertEqual(login, True)
        response = self.client.post(reverse('payment'), self.context)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(Booking.objects.filter(
            account=self.user, 
            flight_ticket_type=FlightTicketType.objects.get(
                flight=self.flight1,
                ticket_type__name=self.context["flight1Class"]
            )
        ).exists())
        self.assertTrue(Booking.objects.filter(
            account=self.user, 
            flight_ticket_type=FlightTicketType.objects.get(
                flight=self.flight2,
                ticket_type__name=self.context["flight2Class"]
            )
        ).exists())
        ticket = Booking.objects.get(
            account=self.user, 
            flight_ticket_type=FlightTicketType.objects.get(
                flight=self.flight1,
                ticket_type__name=self.context["flight1Class"]
            )
        )
        passengers = ticket.passengers.all()
        self.assertEqual(len(passengers), 1)
        self.assertEqual(passengers[0].first_name, 'New')
        self.assertEqual(passengers[0].last_name, 'Tester')
        # Do chưa thanh toán nên mặc định status là PendingCancellation
        self.assertEqual(ticket.status, _('PendingCancellation'))
