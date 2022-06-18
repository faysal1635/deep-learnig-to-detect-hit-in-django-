from django.urls import path

from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('result/', views.result, name='result'),
    path('settings/', views.settings, name='settings'),

    path('profile/', views.profile, name='profile'),

    path('profile/<str:pk>/', views.profilepage, name='profilepage'),
    path('weapon/', views.weapon, name='weapon'),
    path('capture-image/', views.captureimage, name='captureimage'),
    path('detection/', views.detectionResult, name='detectionResult'),


    path('sign-up/', views.signup, name='signup'),
    path('sign-in/', views.signin, name='signin'),
    path('logout/', views.logoutuser, name='logout'),



]
