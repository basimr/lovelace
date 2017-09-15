# -*- coding: utf-8 -*-
# Generated by Django 1.11.1 on 2017-09-15 23:09
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('problems', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='submission',
            name='passed',
            field=models.BooleanField(default=False),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='submission',
            name='date',
            field=models.DateTimeField(auto_now_add=True, verbose_name='submission date'),
        ),
        migrations.AlterField(
            model_name='submission',
            name='file',
            field=models.FileField(upload_to='uploads/%Y/%m/%d', verbose_name='source code file'),
        ),
        migrations.AlterField(
            model_name='submission',
            name='language',
            field=models.CharField(max_length=256, verbose_name='programming language'),
        ),
    ]
