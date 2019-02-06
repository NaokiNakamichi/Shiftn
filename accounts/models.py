from django.db import models
from django.contrib.auth.models import AbstractUser
GENDER_CHOICES = (
    ('1', '女性'),
    ('2', '男性'),
)

class User(AbstractUser):
    gendar = models.CharField("性別", max_length=2, choices=GENDER_CHOICES, blank=True)
    belongs = models.ManyToManyField('boards.Department')
