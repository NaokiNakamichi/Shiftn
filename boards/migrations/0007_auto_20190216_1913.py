# Generated by Django 2.1.2 on 2019-02-16 10:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('boards', '0006_auto_20190207_1639'),
    ]

    operations = [
        migrations.AlterField(
            model_name='shift',
            name='hope',
            field=models.IntegerField(blank=True, choices=[('1', '入れる ○'), ('2', '入れない ✖︎'), ('3', '微妙 ▲')], verbose_name='希望'),
        ),
    ]