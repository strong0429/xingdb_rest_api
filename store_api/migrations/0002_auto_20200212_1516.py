# Generated by Django 3.0.3 on 2020-02-12 07:16

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('store_api', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='xinguser',
            old_name='mobile_phone',
            new_name='mobile',
        ),
    ]
