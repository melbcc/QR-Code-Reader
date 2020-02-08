# Generated by Django 2.1.7 on 2020-02-08 03:18

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('scanner', '0017_address_locblock'),
    ]

    operations = [
        migrations.AddField(
            model_name='event',
            name='loc_block',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='scanner.LocBlock'),
        ),
    ]
