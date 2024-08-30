from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from booking.forms import LoginForm

Account = get_user_model()

class LoginViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = Account.objects.create_user(
            email="tester@example.com",
            username="tester",
            password="12345678",
            phone_number="0123456789"
        )
        self.admin = Account.objects.create_superuser(
            email="admin@example.com",
            username="admin0",
            password="12345678",
            phone_number="0123456789"
        )

    def test_get_login_page(self):
        response = self.client.get(reverse('login'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'login.html')
        self.assertIsInstance(response.context['form'], LoginForm)
    
    def test_post_nonexist_username(self):
        response = self.client.post(reverse('login'), {
            'username': 'tester123',
            'password': '12345678'
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, _('Invalid username and/or password'))

    def test_post_nonexist_password(self):
        response = self.client.post(reverse('login'), {
            'username': 'tester',
            'password': '12345678abc'
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, _('Invalid username and/or password'))

    def test_post_invalid_username(self):
        response = self.client.post(reverse('login'), {
            'username': 'tester!',
            'password': '12345678'
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, _('This username is not valid. Username should contain alphanumeric characters only and have length greater than 6.'))

    def test_post_successful_login_as_user(self):
        response = self.client.post(reverse('login'), {
            'username': 'tester',
            'password': '12345678'
        })
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('index'))
        # Khi quay lại trang login thì sẽ bị chuyển về trang chủ do đã đăng nhập
        response = self.client.get(reverse('login'))
        self.assertRedirects(response, reverse('index'))
        response = self.client.get(reverse('pending_cancellations'))
        # Do không phải admin nên nếu cố truy cập vào trang này sẽ bị buộc đăng xuất
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, '/booking/logout?next=/booking/pending-cancellations/')

    def test_post_login_as_admin(self):
        response = self.client.post(reverse('login'), {
            'username': 'admin0',
            'password': '12345678'
        })
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('index'))
        response = self.client.get(reverse('pending_cancellations'))
        # Vì là admin nên có thể vào được trang pending cancellations duyệt vé được hủy.
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'pending_cancellations.html')
