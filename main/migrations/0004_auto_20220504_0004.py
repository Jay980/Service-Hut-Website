# Generated by Django 2.2.5 on 2022-05-03 18:34

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0003_auto_20220503_2353'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='service',
            name='Service_image',
        ),
        migrations.AlterField(
            model_name='service',
            name='date_published',
            field=models.DateTimeField(default=datetime.datetime(2022, 5, 4, 0, 4, 22, 157166), verbose_name='date published'),
        ),
    ]
