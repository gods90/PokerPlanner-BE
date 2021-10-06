# Generated by Django 2.2 on 2021-10-06 07:44

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Group',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(help_text='Name of the group', max_length=250)),
                ('users', models.ManyToManyField(help_text='Members of the group', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
