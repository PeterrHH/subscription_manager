from django.urls import path
from . import views

urlpatterns = [
    path('add/', views.add_subscription, name='add_subscription'),
    path('', views.home, name='home'),
    path('signup/', views.signup, name='signup'),
]