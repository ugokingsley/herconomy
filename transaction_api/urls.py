from django.urls import path, include
from .views import *
from knox import views as knox_views


urlpatterns = [
    path('register/', register_api , name="register_api"),
    path('login/', login_api, name="login_api"),
    path('get_user/', get_user_api, name="get_user_api"),
    path('logout/', knox_views.LogoutView.as_view()),
    path('logoutall/', knox_views.LogoutAllView.as_view()),

    path('withdraw/', withdrawal, name="withdrawal"),
    path('funds-transfer/', transfer, name="transfer"),

]
