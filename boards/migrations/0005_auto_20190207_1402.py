# Generated by Django 2.1.2 on 2019-02-07 05:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('boards', '0004_auto_20190207_1027'),
    ]

    operations = [
        migrations.AlterField(
            model_name='management',
            name='need',
            field=models.IntegerField(default=1, null=True, verbose_name='必要人数'),
        ),
        migrations.AlterField(
            model_name='management',
            name='part',
            field=models.IntegerField(default=1, null=True, verbose_name='パート数'),
        ),
    ]