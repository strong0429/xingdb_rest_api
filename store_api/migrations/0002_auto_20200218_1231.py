# Generated by Django 3.0.3 on 2020-02-18 04:31

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('store_api', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelTable(
            name='payrecord',
            table='xing_pay_record',
        ),
    ]