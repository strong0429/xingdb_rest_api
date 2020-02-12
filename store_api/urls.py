from django.urls import path

from store_api import views

urlpatterns = [
    path('sms/', views.SMSCode.as_view(), name='sms_code'),
    path('register/', views.UserRegister.as_view(), name='user_register'),
]