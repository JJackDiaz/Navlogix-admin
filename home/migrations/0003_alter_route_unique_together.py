# Generated by Django 5.0.6 on 2024-08-01 00:05

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0002_alter_route_order'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='route',
            unique_together=set(),
        ),
    ]
