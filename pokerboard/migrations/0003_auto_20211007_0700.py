# Generated by Django 2.2 on 2021-10-07 07:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pokerboard', '0002_auto_20211007_0640'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ticket',
            name='estimation_date',
            field=models.DateField(blank=True, help_text='Date on which ticket was estimated', null=True),
        ),
    ]