# Generated by Django 2.2.5 on 2022-05-03 18:23

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0002_auto_20220503_2247'),
    ]

    operations = [
        migrations.AlterField(
            model_name='service',
            name='date_published',
            field=models.DateTimeField(default=datetime.datetime(2022, 5, 3, 23, 53, 34, 949997), verbose_name='date published'),
        ),
    ]