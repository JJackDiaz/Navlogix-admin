# Generated by Django 5.0.6 on 2024-08-16 03:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0005_alter_route_created_at'),
    ]

    operations = [
        migrations.AlterField(
            model_name='route',
            name='created_at',
            field=models.CharField(max_length=20),
        ),
    ]
