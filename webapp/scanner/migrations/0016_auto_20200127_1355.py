# Generated by Django 2.1.7 on 2020-01-27 02:55

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('scanner', '0015_participantstatustype'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='event',
            name='location',
        ),
        migrations.DeleteModel(
            name='Location',
        ),
    ]
