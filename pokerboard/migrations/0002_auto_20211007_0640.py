# Generated by Django 2.2 on 2021-10-07 06:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pokerboard', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='pokerboard',
            name='description',
            field=models.CharField(help_text='Description of Pokerboard.', max_length=100),
        ),
        migrations.AlterField(
            model_name='ticket',
            name='estimation_date',
            field=models.DateField(blank=True, help_text='Date on which ticket was estimated'),
        ),
    ]