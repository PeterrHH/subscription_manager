from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView
from . import views
from . import auth

router = DefaultRouter()
router.register(r'subscriptions', views.SubscriptionViewSet, basename='subscription')

urlpatterns = [
    path('auth/register/', auth.register, name='register'),
    path('auth/login/', auth.login, name='login'),
    path('auth/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('add/', views.subscription_form, name='subscription_form'),
    path('add-api/', views.add_subscription_api, name='add_subscription_api'),
    path('', views.home, name='home'),
    path('signup/', views.signup, name='signup'),
    path('', include(router.urls)),
]