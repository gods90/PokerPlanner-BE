# Generated by Django 2.2 on 2021-11-13 06:55

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('pokerboard', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Session',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, help_text='Time at which object was created')),
                ('updated_at', models.DateTimeField(auto_now=True, help_text='Time at which object was updated')),
                ('title', models.CharField(help_text='Title of the session.', max_length=100)),
                ('status', models.IntegerField(choices=[(0, 'ongoing'), (1, 'hasended')], default=0, help_text='Session ongoing or ended')),
                ('time_started_at', models.DateTimeField(null=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='UserEstimate',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, help_text='Time at which object was created')),
                ('updated_at', models.DateTimeField(auto_now=True, help_text='Time at which object was updated')),
                ('estimation_duration', models.DurationField(help_text='Duration for voting(in secs)')),
                ('estimate', models.PositiveIntegerField(help_text='Value of estimate done by the user.')),
                ('ticket', models.ForeignKey(help_text='Ticket to which estimate belongs.', on_delete=django.db.models.deletion.CASCADE, to='pokerboard.Ticket')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
