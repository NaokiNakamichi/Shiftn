from django.db import models
from accounts.models import User
from django.conf import settings

GENDER_CHOICES = (
    (1, '女性'),
    (0, '男性'),
)

SHIFT_HOPE = (
    (1, '入れる ○'),
    (0, '入れない ×'),
)

SHIFT_DEGREE = (
    (0, 'たくさん入れる'),
    (1, '普通'),
    (2, '少なめで'),
)
EXPERIENCE_CHOICE = (
    (0, '入ったばかり'),
    (1, '入って半年はたった'),
    (2, '入って１年以上はたった')
)
#BoardとTopicとPostは後で削除
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
    message = models.TextField("要望、エラー報告",max_length=4000)

class Department(models.Model): #グループ名、Userがどこのグループに所属しているかのModel
    name =  models.CharField(max_length=30, unique=True)
    password =  models.CharField(max_length=30)
    created_by = models.ForeignKey(User, null=True,on_delete=models.CASCADE)

    def __str__(self):
        return self.name

class Shift(models.Model): #シフトのModel。グループにおけるユーザーのシフトの希望を残すためのModel。年月日単位
    year = models.IntegerField()
    month = models.IntegerField()
    date = models.IntegerField()
    part = models.IntegerField("セクション")
    hope = models.IntegerField("希望",default=1, choices=SHIFT_HOPE)
    user = models.ForeignKey(User, on_delete = models.CASCADE)
    department = models.ForeignKey(Department, on_delete = models.CASCADE)

    def __str__(self):
        return self.department.name + " " + self.user.username + \
         str(self.month) + "月" + str(self.date) + "日" + "part" + str(self.part)

class Management(models.Model): # グループにおけるシフトの設定のModel。何月何日に何part必要なのかを残すためのInt
    year = models.IntegerField()
    month = models.IntegerField()
    date = models.IntegerField()
    part = models.IntegerField("パート数", default=1, null=True)
    department = models.ForeignKey(Department, on_delete = models.CASCADE)

    def __str__(self):
        return self.department.name +  \
         str(self.month) + "月" + str(self.date) + "日"

class ManagementNeed(models.Model):#人数設定
    year = models.IntegerField(null=True,blank=True)
    month = models.IntegerField(null=True,blank=True)
    date = models.IntegerField(null=True,blank=True)
    need = models.IntegerField("必要人数", default=1, null=True)
    part = models.IntegerField("セクション",null=True,blank=True)
    department = models.ForeignKey(Department, on_delete = models.CASCADE)

    def __str__(self):
        return self.department.name +  \
         str(self.month) + "月" + str(self.date) + "日" + str(self.part)

class ShiftDetail(models.Model):
    year = models.IntegerField()
    month = models.IntegerField()
    comment = models.CharField("コメント",max_length=255,null=True,blank=True)
    degree = models.IntegerField("シフト量の希望",default=1, choices=SHIFT_DEGREE,null=True)
    user = models.ForeignKey(User, on_delete = models.CASCADE)
    department = models.ForeignKey(Department, on_delete = models.CASCADE)
    def __str__(self):
        return self.department.name +  \
         str(self.month) + "月" + self.user.username

class ManagementDetail(models.Model):
    year = models.IntegerField(null=True,blank=True)
    month = models.IntegerField(null=True,blank=True)
    relation = models.ForeignKey(Department, on_delete = models.CASCADE)
    min_women = models.IntegerField("女性の最低人数",null=True,blank=True,default=1)
    min_veteran = models.IntegerField("経験者の最低人数",null=True,blank=True,default=1)
    max0 = models.IntegerField("多めに入れる人の最大シフト数",null=True,blank=True,default=11)
    min0 = models.IntegerField("多めに入れる人の最小シフト数",null=True,blank=True,default=1)
    max1 = models.IntegerField("標準の人の最大シフト数",null=True,blank=True,default=9)
    min1 = models.IntegerField("標準の人の最小シフト数",null=True,blank=True,default=1)
    max2 = models.IntegerField("少なめの人の最大シフト数",null=True,blank=True,default=4)
    min2 = models.IntegerField("少なめの人の最小シフト数",null=True,blank=True,default=0)
    renkin_max = models.IntegerField("連勤の最大シフト数",null=True,blank=True,default=3)

class Profile(models.Model):
    experience = models.IntegerField("経験年数",choices=EXPERIENCE_CHOICE)
    user = models.OneToOneField(User,related_name="profile" ,on_delete = models.CASCADE)
