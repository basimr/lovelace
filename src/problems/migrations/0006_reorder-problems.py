# Generated by Django 2.1.5 on 2019-07-08 16:09

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('problems', '0005_extended_submission_model'),
    ]

    operations = [
        migrations.AddField(
            model_name='problem',
            name='order_id',
            field=models.IntegerField(null=True, unique=True, validators=[django.core.validators.MinValueValidator(0)]),
        ),
    ]
