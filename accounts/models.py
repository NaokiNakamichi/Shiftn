from django.db import models
from django.utils import timezone
from django.contrib.auth.models import AbstractUser
GENDER_CHOICES = (
    (1, '女性'),
    (0, '男性'),
)
EXPERIENCE_CHOICE = (
    (0, '入ったばかり'),
    (1, '入って半年はたった'),
    (2, '入って１年以上はたった')
)

class User(AbstractUser):
    gendar = models.IntegerField("性別", choices=GENDER_CHOICES, blank=True,null=True)
    belongs = models.ManyToManyField('boards.Department')
    register_day = models.DateTimeField(default=timezone.now)
    experience = models.IntegerField("経験年数",choices=EXPERIENCE_CHOICE,blank=True,null=True)
