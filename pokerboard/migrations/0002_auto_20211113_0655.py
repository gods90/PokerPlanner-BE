# Generated by Django 2.2 on 2021-11-13 06:55

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('pokerboard', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='pokerboardusergroup',
            name='user',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='pokerboard',
            name='manager',
            field=models.ForeignKey(help_text='Owner of pokerboard.', on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
    ]
