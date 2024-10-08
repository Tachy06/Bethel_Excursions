# Generated by Django 4.2.8 on 2024-08-29 00:31

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('pageLogin', '0008_remove_rooms_bus_bus_2_alter_rooms_bus_bus'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('pagePrincipal', '0003_remove_room_user_room_person1'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='reservation',
            name='number_of_people',
        ),
        migrations.AddField(
            model_name='reservation',
            name='companion',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='pageLogin.companions'),
        ),
        migrations.AlterField(
            model_name='reservation',
            name='user',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL),
        ),
    ]
