# Generated by Django 2.1.2 on 2019-02-25 15:55

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Board',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=30, unique=True)),
                ('description', models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='Department',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=30, unique=True)),
                ('password', models.CharField(max_length=30)),
                ('created_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Management',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('year', models.IntegerField()),
                ('month', models.IntegerField()),
                ('date', models.IntegerField()),
                ('part', models.IntegerField(default=1, null=True, verbose_name='パート数')),
                ('need', models.IntegerField(default=1, null=True, verbose_name='必要人数')),
                ('department', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='boards.Department')),
            ],
        ),
        migrations.CreateModel(
            name='ManagementDetail',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('year', models.IntegerField(blank=True, null=True)),
                ('month', models.IntegerField(blank=True, null=True)),
                ('min_women', models.IntegerField(blank=True, null=True, verbose_name='女性の最低人数')),
                ('max0', models.IntegerField(blank=True, null=True, verbose_name='多めに入れる人の最大シフト数')),
                ('min0', models.IntegerField(blank=True, null=True, verbose_name='多めに入れる人の最小シフト数')),
                ('max1', models.IntegerField(blank=True, null=True, verbose_name='標準の人の最大シフト数')),
                ('min1', models.IntegerField(blank=True, null=True, verbose_name='標準の人の最小シフト数')),
                ('max2', models.IntegerField(blank=True, null=True, verbose_name='少なめの人の最大シフト数')),
                ('min2', models.IntegerField(blank=True, null=True, verbose_name='少なめの人の最小シフト数')),
                ('relation', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='boards.Department')),
            ],
        ),
        migrations.CreateModel(
            name='Post',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('message', models.TextField(max_length=4000)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(null=True)),
                ('created_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='posts', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Profile',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('experience', models.IntegerField(choices=[(0, '入ったばかり'), (1, '入って半年はたった'), (2, '入って１年以上はたった')], verbose_name='経験年数')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='profile', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Shift',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('year', models.IntegerField()),
                ('month', models.IntegerField()),
                ('date', models.IntegerField()),
                ('part', models.IntegerField(verbose_name='セクション')),
                ('hope', models.IntegerField(blank=True, choices=[(1, '入れる ○'), (0, '入れない ✖︎')], default=1, verbose_name='希望')),
                ('department', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='boards.Department')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='ShiftDetail',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('year', models.IntegerField()),
                ('month', models.IntegerField()),
                ('comment', models.CharField(blank=True, max_length=255, null=True, verbose_name='コメント')),
                ('degree', models.IntegerField(choices=[(0, 'たくさん入れる'), (1, '普通'), (2, '少なめで')], default=1, null=True, verbose_name='シフト量の希望')),
                ('department', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='boards.Department')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Topic',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('subject', models.CharField(max_length=255)),
                ('last_update', models.DateTimeField(auto_now_add=True)),
                ('board', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='topics', to='boards.Board')),
                ('starter', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='topics', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddField(
            model_name='post',
            name='topic',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='posts', to='boards.Topic'),
        ),
        migrations.AddField(
            model_name='post',
            name='updated_by',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='+', to=settings.AUTH_USER_MODEL),
        ),
    ]
