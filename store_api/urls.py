from django.urls import path
from rest_framework_jwt.views import obtain_jwt_token

from store_api import views

urlpatterns = [
    path('sms/', views.SMSCode.as_view(), name='sms_code'),
    path('register/', views.UserRegisterView.as_view(), name='user_register'),
    path('login/', obtain_jwt_token, name='user_login'),
    path('stores/', views.StoreListView.as_view(), name='store_list'),
    path('stores/<int:pk>/', views.StoreDetailView.as_view(), name='store_detail'),
]