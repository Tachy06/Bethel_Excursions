# Generated by Django 4.2.8 on 2024-08-29 01:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pagePrincipal', '0004_remove_reservation_number_of_people_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='reservation',
            name='end_date',
        ),
        migrations.RemoveField(
            model_name='reservation',
            name='exclusive',
        ),
        migrations.RemoveField(
            model_name='reservation',
            name='start_date',
        ),
        migrations.AddField(
            model_name='reservation',
            name='companion_name',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
    ]
