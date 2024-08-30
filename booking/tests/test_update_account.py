from django.test import TestCase
from django.utils import timezone
from models import Account
from forms import UpdateAccountForm

class UpdateAccountFormTest(TestCase):

    def setUp(self):
        # Create a sample Account instance to use in tests
        self.account = Account.objects.create(
            username='testuser',
            email='test@example.com',
            phone_number='1234567890',
            first_name='John',
            last_name='Doe',
            gender='Male',
            date_of_birth='1990-01-01',
            role='User',
            status='Active'
        )
    
    def test_form_valid(self):
        form_data = {
            'email': 'newemail@example.com',
            'phone_number': '0987654321',
            'first_name': 'Jane',
            'last_name': 'Doe',
            'gender': 'Female',
            'date_of_birth': '1991-01-01'
        }
        form = UpdateAccountForm(data=form_data, instance=self.account)
        self.assertTrue(form.is_valid())
        updated_account = form.save()
        self.assertEqual(updated_account.email, 'newemail@example.com')
        self.assertEqual(updated_account.phone_number, '0987654321')
        self.assertEqual(updated_account.first_name, 'Jane')
        self.assertEqual(updated_account.last_name, 'Doe')
        self.assertEqual(updated_account.gender, 'Female')
        self.assertEqual(updated_account.date_of_birth, timezone.datetime.strptime('1991-01-01', '%Y-%m-%d').date())

    def test_form_invalid(self):
        form_data = {
            'email': 'newemail@example.com',
            'phone_number': '0987654321',
            'first_name': 'Jane',
            'last_name': 'Doe',
            'gender': 'Unknown',
            'date_of_birth': '1991-01-01'
        }
        form = UpdateAccountForm(data=form_data, instance=self.account)
        self.assertFalse(form.is_valid())
        self.assertIn('gender', form.errors)

    def test_form_no_data(self):
        form = UpdateAccountForm(data={}, instance=self.account)
        self.assertFalse(form.is_valid())
        self.assertIn('email', form.errors)
        self.assertIn('first_name', form.errors)

    def test_form_save(self):
        form_data = {
            'email': 'save@example.com',
            'phone_number': '1122334455',
            'first_name': 'Saved',
            'last_name': 'User',
            'gender': 'Male',
            'date_of_birth': '1992-02-02'
        }
        form = UpdateAccountForm(data=form_data, instance=self.account)
        if form.is_valid():
            updated_account = form.save()
            self.assertEqual(updated_account.email, 'save@example.com')
            self.assertEqual(updated_account.phone_number, '1122334455')
            self.assertEqual(updated_account.first_name, 'Saved')
            self.assertEqual(updated_account.last_name, 'User')
            self.assertEqual(updated_account.gender, 'Male')
            self.assertEqual(updated_account.date_of_birth, timezone.datetime.strptime('1992-02-02', '%Y-%m-%d').date())
        else:
            self.fail('Form should be valid but is not.')
