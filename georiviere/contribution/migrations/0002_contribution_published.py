# Generated by Django 3.1.14 on 2023-05-30 13:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('contribution', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='contribution',
            name='published',
            field=models.BooleanField(default=False, help_text='Make it visible on portal', verbose_name='Published'),
        ),
    ]
