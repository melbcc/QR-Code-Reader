# Generated by Django 2.1.7 on 2019-03-29 11:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('scanner', '0013_event_end_time'),
    ]

    operations = [
        migrations.AlterField(
            model_name='event',
            name='end_time',
            field=models.DateTimeField(blank=True, null=True, verbose_name='end time'),
        ),
    ]
