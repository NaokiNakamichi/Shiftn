# Generated by Django 2.1.2 on 2019-02-26 15:50

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('boards', '0006_auto_20190227_0021'),
    ]

    operations = [
        migrations.AlterField(
            model_name='managementneed',
            name='department',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='boards.Department'),
        ),
    ]