# -*- coding: utf-8 -*-
# Generated by Django 1.11.1 on 2017-06-07 07:43
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('farmapp', '0004_crop_imagepath'),
    ]

    operations = [
        migrations.CreateModel(
            name='Cart_session',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('weight', models.FloatField()),
                ('time', models.DateTimeField()),
            ],
            options={
                'verbose_name_plural': 'cart sessions',
            },
        ),
        migrations.AlterModelOptions(
            name='cart',
            options={'verbose_name_plural': 'cart'},
        ),
        migrations.AlterModelOptions(
            name='crop',
            options={'verbose_name_plural': 'crops'},
        ),
        migrations.AlterModelOptions(
            name='inventory',
            options={'verbose_name_plural': 'inventories'},
        ),
        migrations.AlterModelOptions(
            name='machine',
            options={'verbose_name_plural': 'machines'},
        ),
        migrations.AlterModelOptions(
            name='order',
            options={'verbose_name_plural': 'orders'},
        ),
        migrations.AlterModelOptions(
            name='produce',
            options={'verbose_name_plural': 'produce'},
        ),
        migrations.AlterModelOptions(
            name='trough',
            options={'verbose_name_plural': 'troughs'},
        ),
        migrations.AlterModelOptions(
            name='user',
            options={'verbose_name_plural': 'users'},
        ),
        migrations.RemoveField(
            model_name='cart',
            name='crop_id',
        ),
        migrations.RemoveField(
            model_name='cart',
            name='time',
        ),
        migrations.RemoveField(
            model_name='cart',
            name='weight',
        ),
        migrations.AlterField(
            model_name='order',
            name='cart_id',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='farmapp.Cart_session'),
        ),
        migrations.AddField(
            model_name='cart_session',
            name='cart_id',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='farmapp.Cart'),
        ),
        migrations.AddField(
            model_name='cart_session',
            name='crop_id',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='farmapp.Crop'),
        ),
    ]
