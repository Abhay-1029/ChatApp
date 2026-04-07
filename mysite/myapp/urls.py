from django.contrib.auth.views import LogoutView
from django.urls import path
from . import views
urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('signup/', views.signup_view, name='signup'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('<slug:slug>/delete/', views.delete_room, name='delete_room'),
    path('<slug:slug>/leave/', views.leave_room, name='leave_room'),
    path('<slug:slug>/upload/', views.upload_attachment, name='upload_attachment'),
    path('',views.index,name='index'),
    path('<slug:slug>/',views.chatroom,name='chatroom'),
]
