# Generated by Django 3.2.25 on 2024-08-26 16:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('booking', '0012_auto_20240826_2325'),
    ]

    operations = [
        migrations.AlterField(
            model_name='booking',
            name='status',
            field=models.CharField(choices=[('Confirmed', 'Confirmed'), ('Canceled', 'Canceled'), ('PendingCancellation', 'PendingCancellation'), ('DeniedCancellation', 'DeniedCancellation')], default='PendingCancellation', max_length=20),
        ),
    ]
