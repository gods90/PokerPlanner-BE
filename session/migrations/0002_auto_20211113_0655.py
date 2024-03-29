# Generated by Django 2.2 on 2021-11-13 06:55

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('pokerboard', '0002_auto_20211113_0655'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('session', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='userestimate',
            name='user',
            field=models.ForeignKey(help_text='User which has estimated the ticket.', on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='session',
            name='pokerboard',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='session', to='pokerboard.Pokerboard'),
        ),
    ]
