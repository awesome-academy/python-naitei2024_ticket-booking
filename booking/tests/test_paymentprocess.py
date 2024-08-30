from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import check_password
from django.utils.translation import gettext_lazy as _
from booking.forms import SignUpForm
from booking.constants import STATUS_CHOICES, BOOKING_STATUS
from booking.models import (
    Account, Flight, FlightTicketType, TicketType, 
    Airport, Booking, Payment, Card, Passenger
)
from django.utils.dateparse import parse_datetime, parse_date

class PaymentProcessTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = Account.objects.create_user(
            email="tester@example.com",
            username="tester",
            password="12345678",
            phone_number="0123456789"
        )
        self.user2 = Account.objects.create_user(
            email="tester2@example.com",
            username="tester2",
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
            arrival_airport=self.airport3,
            departure_time=parse_datetime('2069-09-01T15:00:00+0000'),
            arrival_time=parse_datetime('2069-09-01T16:00:00+0000')
        )
        self.flight4 = Flight.objects.create(
            flight_number='A336',
            airline='TestAir4',
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
        self.passenger1 = Passenger.objects.create(
            first_name='New',
            last_name='Tester',
            gender='Male',
            date_of_birth='2003-10-16',
            nationality='Vietnam',
            passport_number='None',
            passport_from_country='None'
        )
        self.booking1 = Booking.objects.create(
            account=self.user,
            flight_ticket_type=FlightTicketType.objects.get(
                flight=self.flight1, 
                ticket_type=self.tickettype1
            ),
            seat_number='1',
        )
        self.booking1.passengers.add(self.passenger1)
        self.booking2 = Booking.objects.create(
            account=self.user,
            flight_ticket_type=FlightTicketType.objects.get(
                flight=self.flight2, 
                ticket_type=self.tickettype1
            ),
            seat_number='1',
        )
        self.booking2.passengers.add(self.passenger1)
        self.booking3 = Booking.objects.create(
            account=self.user,
            flight_ticket_type=FlightTicketType.objects.get(
                flight=self.flight1, 
                ticket_type=self.tickettype1
            ),
            seat_number='1',
            status=dict(BOOKING_STATUS)["Confirmed"]
        )
        self.booking3.passengers.add(self.passenger1)
        self.booking4 = Booking.objects.create(
            account=self.user2,
            flight_ticket_type=FlightTicketType.objects.get(
                flight=self.flight1, 
                ticket_type=self.tickettype1
            ),
            seat_number='1',
        )
        self.booking4.passengers.add(self.passenger1)
        self.context = {
            'ticket1': self.booking1.booking_id,
            'ticket2': self.booking2.booking_id,
            'cardNumber': '9876678998766789987',
            'cardHolderName': 'New Tester',
            'expMonth': '01',
            'expYear': '2060',
            'cardType': 'Visa',
        }

    def test_post_process_user_not_authenticated(self):
        response = self.client.post(reverse('process'), self.context)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/booking/login?next=/booking/process')
    
    def test_post_process_ticket_id_is_missing(self):
        login = self.client.login(username='tester', password='12345678')
        self.assertTrue(login)
        self.context["ticket1"] = ""
        response = self.client.post(reverse('process'), self.context)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'payment.html')
        messages = list(response.wsgi_request._messages)
        self.assertEqual(messages[0].message, _("This ticket is not exist."))

    def test_post_process_ticket_id_is_invalid(self):
        login = self.client.login(username='tester', password='12345678')
        self.assertTrue(login)
        self.context["ticket1"] = "abc"
        response = self.client.post(reverse('process'), self.context)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'payment.html')
        messages = list(response.wsgi_request._messages)
        self.assertEqual(messages[0].message, _("This ticket is not exist."))
    
    # Booking số 3 đã được Confirmed (hoặc một trạng thái khác ngoài PendingCancellation)
    def test_post_process_ticket_is_confirmed_already(self):
        login = self.client.login(username='tester', password='12345678')
        self.assertTrue(login)
        self.context["ticket1"] = self.booking3.booking_id
        response = self.client.post(reverse('process'), self.context)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'payment.html')
        messages = list(response.wsgi_request._messages)
        self.assertEqual(messages[0].message, _("This ticket is not valid."))
    
    # Booking số 4 là booking của 1 user khác (user2)
    def test_post_process_ticket_is_from_another_user(self):
        login = self.client.login(username='tester', password='12345678')
        self.assertTrue(login)
        self.context["ticket1"] = self.booking4.booking_id
        response = self.client.post(reverse('process'), self.context)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'payment.html')
        messages = list(response.wsgi_request._messages)
        self.assertEqual(messages[0].message, _("This ticket is not valid."))

    def test_post_process_card_number_is_missing(self):
        login = self.client.login(username='tester', password='12345678')
        self.assertTrue(login)
        self.context["cardNumber"] = ""
        response = self.client.post(reverse('process'), self.context)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'payment.html')
        messages = list(response.wsgi_request._messages)
        self.assertEqual(messages[0].message, _("Please input your card number."))

    # Số thẻ không được chứa ký tự khác ngoài số
    def test_post_process_card_number_is_invalid(self):
        login = self.client.login(username='tester', password='12345678')
        self.assertTrue(login)
        self.context["cardNumber"] = "-147abc@%"
        response = self.client.post(reverse('process'), self.context)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'payment.html')
        messages = list(response.wsgi_request._messages)
        self.assertEqual(messages[0].message, _("Your card number is not valid. It must contain numbers only."))
    
    def test_post_process_card_number_max_length_is_20(self):
        login = self.client.login(username='tester', password='12345678')
        self.assertTrue(login)
        self.context["cardNumber"] = "123456789987654321123"
        response = self.client.post(reverse('process'), self.context)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'payment.html')
        messages = list(response.wsgi_request._messages)
        self.assertEqual(messages[0].message, _("Your card number is not valid. Its length must be less than 20."))

    def test_post_process_card_holder_name_is_missing(self):
        login = self.client.login(username='tester', password='12345678')
        self.assertTrue(login)
        self.context["cardHolderName"] = ""
        response = self.client.post(reverse('process'), self.context)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'payment.html')
        messages = list(response.wsgi_request._messages)
        self.assertEqual(messages[0].message, _("Please input your card holder's name."))

    # Tên chủ thẻ chỉ chứa chữ cái
    def test_post_process_card_holder_name_is_invalid(self):
        login = self.client.login(username='tester', password='12345678')
        self.assertTrue(login)
        self.context["cardHolderName"] = "Abc123***"
        response = self.client.post(reverse('process'), self.context)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'payment.html')
        messages = list(response.wsgi_request._messages)
        self.assertEqual(messages[0].message, _("Your card holder's name is not valid."))

    def test_post_process_expire_month_is_missing(self):
        login = self.client.login(username='tester', password='12345678')
        self.assertTrue(login)
        self.context["expMonth"] = ""
        response = self.client.post(reverse('process'), self.context)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'payment.html')
        messages = list(response.wsgi_request._messages)
        self.assertEqual(messages[0].message, _("Please select your card's expire month."))

    def test_post_process_expire_month_is_invalid(self):
        login = self.client.login(username='tester', password='12345678')
        self.assertTrue(login)
        self.context["expMonth"] = "abc"
        response = self.client.post(reverse('process'), self.context)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'payment.html')
        messages = list(response.wsgi_request._messages)
        self.assertEqual(messages[0].message, _("Your expire month is not valid."))

    def test_post_process_expire_month_is_out_of_range_1_to_12(self):
        login = self.client.login(username='tester', password='12345678')
        self.assertTrue(login)
        self.context["expMonth"] = "13"
        response = self.client.post(reverse('process'), self.context)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'payment.html')
        messages = list(response.wsgi_request._messages)
        self.assertEqual(messages[0].message, _("Your expire month is not valid."))

    def test_post_process_expire_year_is_missing(self):
        login = self.client.login(username='tester', password='12345678')
        self.assertTrue(login)
        self.context["expYear"] = ""
        response = self.client.post(reverse('process'), self.context)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'payment.html')
        messages = list(response.wsgi_request._messages)
        self.assertEqual(messages[0].message, _("Please select your card's expire year."))

    def test_post_process_expire_year_is_invalid(self):
        login = self.client.login(username='tester', password='12345678')
        self.assertTrue(login)
        self.context["expYear"] = "abc"
        response = self.client.post(reverse('process'), self.context)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'payment.html')
        messages = list(response.wsgi_request._messages)
        self.assertEqual(messages[0].message, _("Your expire year is not valid."))

    def test_post_process_expire_year_is_out_of_range_2024_to_2060(self):
        login = self.client.login(username='tester', password='12345678')
        self.assertTrue(login)
        self.context["expYear"] = "2061"
        response = self.client.post(reverse('process'), self.context)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'payment.html')
        messages = list(response.wsgi_request._messages)
        self.assertEqual(messages[0].message, _("Your expire year is not valid."))

    def test_post_process_card_is_expired(self):
        login = self.client.login(username='tester', password='12345678')
        self.assertTrue(login)
        self.context["expYear"] = "2024"
        self.context["expMonth"] = "08"
        response = self.client.post(reverse('process'), self.context)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'payment.html')
        messages = list(response.wsgi_request._messages)
        self.assertEqual(messages[0].message, _("Your card is expired. Please choose another card."))

    def test_post_process_card_type_is_missing(self):
        login = self.client.login(username='tester', password='12345678')
        self.assertTrue(login)
        self.context["cardType"] = ""
        response = self.client.post(reverse('process'), self.context)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'payment.html')
        messages = list(response.wsgi_request._messages)
        self.assertEqual(messages[0].message, _("Please select your card's type."))

    # Không phải Visa hay MasterCard
    def test_post_process_card_type_is_invalid(self):
        login = self.client.login(username='tester', password='12345678')
        self.assertTrue(login)
        self.context["cardType"] = "PayPal"
        response = self.client.post(reverse('process'), self.context)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'payment.html')
        messages = list(response.wsgi_request._messages)
        self.assertEqual(messages[0].message, _("Your card's type is not valid."))

    def test_post_process_successful_payment(self):
        login = self.client.login(username='tester', password='12345678')
        self.assertTrue(login)
        response = self.client.post(reverse('process'), self.context)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'payment_process.html')

        # Kiểm tra xem có thông tin thẻ chưa
        self.assertTrue(Card.objects.filter(user=self.user).exists())
        card = Card.objects.get(user=self.user)
        self.assertEqual(card.card_number, '9876678998766789987')
        self.assertEqual(card.cardholder_name, 'New Tester')
        self.assertEqual(card.card_type, 'Visa')

        # Kiểm tra xem có thông tin giao dịch chưa
        self.assertTrue(Payment.objects.filter(booking=self.booking1).exists())
        self.assertTrue(Payment.objects.filter(booking=self.booking2).exists())
        payment1 = Payment.objects.get(booking=self.booking1)
        payment2 = Payment.objects.get(booking=self.booking2)
        self.assertEqual(payment1.card, card)
        self.assertEqual(payment2.card, card)
        self.assertEqual(float(payment1.amount), 2400000)

        # Kiểm tra trạng thái vé đã chuyển sang Confirmed chưa
        self.assertEqual(payment1.booking.status, _('Confirmed'))
        self.assertEqual(payment2.booking.status, _('Confirmed'))
