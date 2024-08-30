from django.test import TestCase
from forms import PasswordResetRequestForm

class PasswordResetRequestFormTest(TestCase):
    
    def test_form_valid(self):
        # Valid email
        form_data = {
            'email': 'validemail@example.com'
        }
        form = PasswordResetRequestForm(data=form_data)
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data['email'], 'validemail@example.com')
    
    def test_form_invalid_email(self):
        # Invalid email
        form_data = {
            'email': 'invalidemail'
        }
        form = PasswordResetRequestForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('email', form.errors)
    
    def test_form_missing_email(self):
        # Missing email
        form_data = {
            # No email provided
        }
        form = PasswordResetRequestForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('email', form.errors)
    
    def test_form_empty_input(self):
        # Empty input
        form_data = {
            'email': ''
        }
        form = PasswordResetRequestForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('email', form.errors)
