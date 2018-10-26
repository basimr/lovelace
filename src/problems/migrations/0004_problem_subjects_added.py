# Generated by Django 2.1.2 on 2018-10-20 21:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('problems', '0003_fixed_bug_in_timesink'),
    ]

    operations = [
        migrations.AddField(
            model_name='problem',
            name='subject',
            field=models.CharField(choices=[('physics', 'Physics'), ('math', 'Math'), ('earth science', 'Earth science'), ('chemistry', 'Chemistry'), ('biology', 'Biology'), ('astronomy', 'Astronomy'), ('engineering', 'Engineering'), ('computer science', 'Computer science')], default='physics', max_length=32),
        ),
    ]