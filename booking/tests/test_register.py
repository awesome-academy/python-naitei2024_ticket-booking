from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import check_password
from django.utils.translation import gettext_lazy as _
from booking.forms import SignUpForm
from booking.constants import STATUS_CHOICES
from booking.models import Account
# Account = get_user_model()

class SignUpViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.active_user = Account.objects.create_user(
            email="tester@example.com",
            username="tester",
            password="12345678",
            phone_number="0123456789"
        )
        self.inactive_user = Account.objects.create_user(
            email="tester2@example.com",
            username="tester2",
            password="12345678",
            phone_number="0123456789",
            status=dict(STATUS_CHOICES)['Suspended']
        )

    def test_get_register_page(self):
        response = self.client.get(reverse('register'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'register.html')
        self.assertIsInstance(response.context['form'], SignUpForm)
    
    def test_post_successful_register(self):
        response = self.client.post(reverse('register'), {
            'username': 'tester3',
            'email': 'tester3@example.com',
            'phone_number': '0123456789',
            'password': '12345678',
            'confirm_password': '12345678'
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Account.objects.filter(username='tester3').exists())
        user = Account.objects.get(username='tester3')
        self.assertEqual(user.email, 'tester3@example.com')
        self.assertEqual(user.phone_number, '0123456789')
        self.assertTrue(check_password('12345678', user.password))

    def test_post_too_short_username(self):
        response = self.client.post(reverse('register'), {
            'username': 'test',
            'email': 'tester3@example.com',
            'phone_number': '0123456789',
            'password': '12345678',
            'confirm_password': '12345678'
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, _("Ensure this value has at least 6 characters"))
    
    # Invalid username khi có chứa các ký tự đặc biệt
    def test_post_invalid_username(self):
        response = self.client.post(reverse('register'), {
            'username': 'test%^$',
            'email': 'tester3@example.com',
            'phone_number': '0123456789',
            'password': '12345678',
            'confirm_password': '12345678'
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, _("Enter a valid value."))

    def test_post_invalid_phone_number(self):
        response = self.client.post(reverse('register'), {
            'username': 'tester3',
            'email': 'tester3@example.com',
            'phone_number': '01234abc2',
            'password': '12345678',
            'confirm_password': '12345678'
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, _("Enter a valid value."))

    def test_post_password_mismatch(self):
        response = self.client.post(reverse('register'), {
            'username': 'tester3',
            'email': 'tester3@example.com',
            'phone_number': '0123456789',
            'password': '12345678',
            'confirm_password': '12345678abc'
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, _("Password and confirm password are not the same."))

    def test_post_user_already_exists(self):
        response = self.client.post(reverse('register'), {
            'username': 'tester2',
            'email': 'tester3@example.com',
            'phone_number': '0123456789',
            'password': '12345678',
            'confirm_password': '12345678abc'
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, _("User with this Username already exists."))
