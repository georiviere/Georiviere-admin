# Generated by Django 3.1.14 on 2022-12-13 10:00

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('knowledge', '0014_auto_20221213_0949'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='vegetation',
            name='strata',
        ),
    ]
