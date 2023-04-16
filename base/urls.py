from django.urls import path
from . import views

appname = 'base'

urlpatterns = [
    # --- Room routes
    path('', views.home, name='home'),
    path('room/create', views.create_room, name='create-room'),
    path('room/<str:pk>', views.room, name='room'),
    path('room/update/<str:pk>', views.update_room, name='update-room'),
    path('room/delete-message/<str:pk>', views.delete_message, name='delete-message'),
    path('room/delete/<str:pk>', views.delete_room, name='delete-room'),

    path('topics', views.topics_page, name='topics'),
    path('activity', views.activity_page, name='activity'),

    # --- User routes
    path('user/update', views.update_user, name='user-update'),
    path('user/<str:pk>', views.user_profile, name='user-profile'),

    # --- User authentication routes
    path('login', views.login_page, name='login'),
    path('logout', views.logout_page, name='logout'),
    path('register', views.register_page, name='register'),
]
