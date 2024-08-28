from django.utils.translation import gettext_lazy as _

MAX_LENGTH_NAME = 255
MAX_LENGTH_CHOICES = 255

GENDER_CHOICES = [
    ('Male', _('Male')),
    ('Female', _('Female')),
    ('Other', _('Other')),
]

STATUS_CHOICES = [
    ('Active', _('Active')),
    ('Suspended', _('Suspended')),
]

ROLE_CHOICES = [
    ('Admin', _('Admin')),
    ('Member', _('Member')),
]

CARD_TYPE_CHOICES = [
    ('Visa', _('Visa')),
    ('MasterCard', _('MasterCard')),
]

BOOKING_STATUS = [
    ('Confirmed', _('Confirmed')),
    ('Canceled', _('Canceled')),
    ('PendingCancellation', _('PendingCancellation')),
    ('DeniedCancellation', _('DeniedCancellation'))
]

PAYMENT_METHOD_CHOICES = [
        ('Credit Card', _('Credit Card')),
        ('PayPal', _('PayPal')),
]

REGEX_PATTERN = r"^[\w]+$"

REGEX_PATTERN_NAME = r"^[a-zA-Z ]+$"

REGEX_PATTERN_NUMBER = r"^[0-9]+$"

REGEX_PATTERN_EMAIL = r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)"

PRICE_FORMAT = '{:,.0f}'

ISO = 'ISO-8859-1'
