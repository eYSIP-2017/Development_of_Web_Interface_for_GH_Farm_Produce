# -*- coding: utf-8 -*-
# Generated by Django 1.11.1 on 2017-06-27 14:21
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('farmapp', '0002_auto_20170627_1204'),
    ]

    operations = [
        migrations.AddField(
            model_name='produce',
            name='show_image',
            field=models.BooleanField(default=True),
        ),
    ]
