# Generated by Django 2.2 on 2021-10-13 05:20

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('group', '__first__'),
    ]

    operations = [
        migrations.CreateModel(
            name='Pokerboard',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(help_text='Name of Pokerboard.', max_length=50)),
                ('description', models.CharField(help_text='Description of Pokerboard.', max_length=100)),
                ('configuration', models.IntegerField(choices=[(1, 'Series'), (2, 'Even'), (3, 'Odd'), (4, 'Fibonacci')], default=1, help_text='Estimation type.')),
                ('status', models.PositiveSmallIntegerField(choices=[(1, 'Created'), (2, 'Started'), (3, 'Ended')], default=1, help_text='Default pokerboard status is created.')),
                ('manager', models.ForeignKey(help_text='Owner of pokerboard.', on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Ticket',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ticket_id', models.CharField(help_text='Ticket ID imported from JIRA.', max_length=100, unique=True)),
                ('order', models.PositiveSmallIntegerField(help_text='Rank of ticket.')),
                ('estimation_date', models.DateField(blank=True, help_text='Date on which ticket was estimated', null=True)),
                ('status', models.IntegerField(choices=[(0, 'notstarted'), (0, 'ongoing'), (1, 'hasended')], default=0, help_text='Default ticket status is not started.')),
                ('pokerboard', models.ForeignKey(help_text='Pokerboard to which ticket belongs.', on_delete=django.db.models.deletion.CASCADE, to='pokerboard.Pokerboard')),
            ],
        ),
        migrations.CreateModel(
            name='UserEstimate',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('estimation_duration', models.DurationField(help_text='Duration for voting(in secs)')),
                ('estimate', models.PositiveIntegerField(help_text='Value of estimate done by the user.')),
                ('ticket', models.ForeignKey(help_text='Ticket to which estimate belongs.', on_delete=django.db.models.deletion.CASCADE, to='pokerboard.Ticket')),
                ('user', models.ForeignKey(help_text='User which has estimated the ticket.', on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='PokerboardUserMapping',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user_role', models.IntegerField(choices=[(0, 'PLAYER'), (1, 'MANAGER'), (2, 'SPECTATOR')], default=(0, 'PLAYER'), help_text='Default user role is player.')),
                ('pokerboard', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='pokerboard.Pokerboard')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Invite',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user_role', models.IntegerField(choices=[(0, 'PLAYER'), (1, 'MANAGER'), (2, 'SPECTATOR')], default=(0, 'PLAYER'), help_text='Default user role is player')),
                ('is_accepted', models.BooleanField(default=False)),
                ('group', models.ForeignKey(help_text='Group which is invited.', null=True, on_delete=django.db.models.deletion.CASCADE, to='group.Group')),
                ('pokerboard', models.ForeignKey(help_text='Pokerboard of which invite has been sent.', on_delete=django.db.models.deletion.CASCADE, to='pokerboard.Pokerboard')),
                ('user', models.ForeignKey(help_text='User which is invited.', on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
