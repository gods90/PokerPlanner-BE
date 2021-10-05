# Generated by Django 2.2 on 2021-10-05 06:09

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('group', '0002_group_users'),
        ('pokerboard', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='userestimate',
            name='user',
            field=models.ForeignKey(help_text='User which has estimated the ticket.', on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='ticket',
            name='pokerboard',
            field=models.ForeignKey(help_text='Pokerboard to which ticket belongs.', on_delete=django.db.models.deletion.CASCADE, to='pokerboard.Pokerboard'),
        ),
        migrations.AddField(
            model_name='pokerboardusermapping',
            name='pokerboard',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='pokerboard.Pokerboard'),
        ),
        migrations.AddField(
            model_name='pokerboardusermapping',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='pokerboard',
            name='manager',
            field=models.ForeignKey(help_text='Owner of pokerboard.', on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='invite',
            name='group',
            field=models.ForeignKey(help_text='Group which is invited.', null=True, on_delete=django.db.models.deletion.CASCADE, to='group.Group'),
        ),
        migrations.AddField(
            model_name='invite',
            name='pokerboard',
            field=models.ForeignKey(help_text='Pokerboard of which invite has been sent.', on_delete=django.db.models.deletion.CASCADE, to='pokerboard.Pokerboard'),
        ),
        migrations.AddField(
            model_name='invite',
            name='user',
            field=models.ForeignKey(help_text='User which is invited.', on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
    ]
