from django.contrib import admin
from accounts.models import User
from .models import Board,Department,Management
from django.contrib.auth.admin import UserAdmin

admin.site.register(Board)
admin.site.register(Management)
admin.site.register(Department)
admin.site.register(User, UserAdmin)
