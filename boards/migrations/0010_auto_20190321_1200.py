# Generated by Django 2.1.2 on 2019-03-21 03:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('boards', '0009_auto_20190227_0708'),
    ]

    operations = [
        migrations.AlterField(
            model_name='managementdetail',
            name='renkin_max',
            field=models.IntegerField(blank=True, default=3, null=True, verbose_name='連勤の最大シフト数'),
        ),
    ]