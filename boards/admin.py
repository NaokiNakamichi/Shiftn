from django.contrib import admin
from accounts.models import User
from .models import Board,Department,Management,Shift,ShiftDetail,ManagementDetail,ManagementNeed
from django.contrib.auth.admin import UserAdmin

admin.site.register(Board)
admin.site.register(Management)
admin.site.register(Department)
admin.site.register(Shift)
admin.site.register(ManagementDetail)
admin.site.register(ManagementNeed)
admin.site.register(ShiftDetail)

@admin.register(User)
class AdminUserAdmin(UserAdmin):

    fieldsets = (
        (None, {'fields': ('username','email', 'gendar', 'password','experience','register_day')}),
        (('Personal info'), {'fields': ('first_name', 'last_name')}),
        (('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser',
                                       'groups', 'user_permissions')}),
        (('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )
    list_display = ('username', 'email', 'is_staff', 'gendar','experience')
    search_fields = ('username', 'email')
