# Generated by Django 2.2 on 2021-10-13 11:42

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('group', '0002_auto_20211011_0542'),
        ('pokerboard', '0004_auto_20211007_0718'),
    ]

    operations = [
        migrations.CreateModel(
            name='PokerboardUserGroup',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('role', models.IntegerField(choices=[(0, 'PLAYER'), (1, 'MANAGER'), (2, 'SPECTATOR')], default=(0, 'PLAYER'), help_text='Default user role is player.')),
                ('group', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='group.Group')),
                ('pokerboard', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='pokerboard.Pokerboard')),
                ('user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Session',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.IntegerField(choices=[(0, 'ongoing'), (1, 'hasended')], default=0, help_text='Session ongoing or ended')),
                ('pokerboard', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='pokerboard.Pokerboard')),
            ],
        ),
        migrations.DeleteModel(
            name='PokerboardUserMapping',
        ),
    ]