from django.db import models
from accounts.models import User
from django.conf import settings

GENDER_CHOICES = (
    ('1', '女性'),
    ('2', '男性'),
)

SHIFT_HOPE = (
    ('1', '入れる ○'),
    ('2', '入れない ✖︎'),
    ('3', '微妙 ▲'),
)

class Board(models.Model):
    name = models.CharField(max_length=30, unique=True)
    description = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class Topic(models.Model):
    subject = models.CharField(max_length=255)
    last_update = models.DateTimeField(auto_now_add=True)
    board = models.ForeignKey(Board,related_name='topics',on_delete=models.CASCADE)
    starter = models.ForeignKey(User,related_name='topics',on_delete=models.CASCADE)

class Post(models.Model):
    message = models.TextField(max_length=4000)
    topic = models.ForeignKey(Topic, related_name='posts',on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(null=True)
    created_by = models.ForeignKey(User, related_name='posts',on_delete=models.CASCADE)
    updated_by = models.ForeignKey(User, null=True, related_name='+',on_delete=models.CASCADE)

class Department(models.Model):
    name =  models.CharField(max_length=30, unique=True)
    password =  models.CharField(max_length=30)
    created_by = models.ForeignKey(User, null=True,on_delete=models.CASCADE)

    def __str__(self):
        return self.name

class Shift(models.Model):
    year = models.IntegerField()
    month = models.IntegerField()
    date = models.IntegerField()
    part = models.IntegerField("セクション")
    hope = models.CharField("希望", max_length=3, choices=SHIFT_HOPE, blank=True)
    user = models.ForeignKey(User, on_delete = models.CASCADE)
    department = models.ForeignKey(Department, on_delete = models.CASCADE)

    def __str__(self):
        return self.department.name + " " + self.user.username + \
         str(self.month) + "月" + str(self.date) + "日" + "part" + str(self.part)

class Management(models.Model):
    year = models.IntegerField()
    month = models.IntegerField()
    date = models.IntegerField()
    part = models.IntegerField("パート数", default=1, null=True)
    need = models.IntegerField("必要人数", default=1, null=True)
    department = models.ForeignKey(Department, on_delete = models.CASCADE)

    def __str__(self):
        return self.department.name +  \
         str(self.month) + "月" + str(self.date) + "日"
