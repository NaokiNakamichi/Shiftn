from django.db import models
from django.contrib.auth.models import AbstractUser
GENDER_CHOICES = (
    (1, '女性'),
    (0, '男性'),
)

class User(AbstractUser):
    gendar = models.IntegerField("性別", choices=GENDER_CHOICES, blank=True)
    belongs = models.ManyToManyField('boards.Department')
