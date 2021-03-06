"""myproject URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.conf.urls import url
from accounts import views as accounts_views
from django.contrib.auth import views as auth_views
from boards import views
urlpatterns = [
    path('', views.home, name='home'),
    path('boards/user_home',views.user_home,name='user_home'),
    path('boards/demand',views.demand,name='demand'),
    path('boards/group_create',views.group_create,name='group_create'),
    path('boards/group_page/<int:pk>',views.group_page,name='group_page'),
    path('boards/group_page/<int:pk>/shift_show',views.shift_show,name='shift_show'),
    path('boards/group_page/<int:pk>/submit/',views.shift_submit,name='shift_submit'),
    path('boards/group_page/<int:pk>/detail/',views.shift_detail,name='shift_detail'),
    path('boards/group_page/<int:pk>/create/',views.shift_create,name='shift_create'),
    path('boards/group_page/<int:pk>/management_detail/',views.management_detail,name='management_detail'),
    path('boards/group_page/<int:pk>/management_part/',views.management_part,name='management_part'),
    path('boards/group_page/<int:pk>/management_need/',views.management_need,name='management_need'),
    path('boards/group_page/<int:pk>/management/',views.management,name='management'),
    path('boards/group_login/',views.group_login,name='group_login'),
    path('admin/', admin.site.urls),
    path('boards/<int:pk>/topics/<int:topic_pk>/reply/', views.reply_topic, name='reply_topic'),
    path('boards/<int:pk>/topics/<int:topic_pk>/', views.topic_posts, name='topic_posts'),
    path('boards/<int:pk>/',views.board_topics, name='board_topics'),
    path('boards/<int:pk>/new/', views.new_topic, name='new_topic'),
    path('signup/',accounts_views.signup, name='signup'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),

]
