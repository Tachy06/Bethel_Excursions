# Generated by Django 4.2.8 on 2024-08-10 03:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pageLogin', '0003_asiento_companion'),
    ]

    operations = [
        migrations.AddField(
            model_name='asiento',
            name='companion_name',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
    ]
