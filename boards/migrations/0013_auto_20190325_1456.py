# Generated by Django 2.1.2 on 2019-03-25 05:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('boards', '0012_auto_20190325_1250'),
    ]

    operations = [
        migrations.AlterField(
            model_name='shift',
            name='hope',
            field=models.IntegerField(choices=[(1, '入れる ○'), (0, '入れない ×')], default=1, verbose_name='希望'),
        ),
    ]