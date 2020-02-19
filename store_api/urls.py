from django.urls import path
from rest_framework_jwt.views import obtain_jwt_token

from store_api import views_user, views_store

urlpatterns = [
    path('token/', obtain_jwt_token, name='token'),
    path('sms/', views_user.SMSCodeView.as_view(), name='sms_code'),
    path('register/', views_user.UserRegisterView.as_view(), name='user_register'),
    path('login/', views_user.UserLoginView.as_view(), name='user_login'),
    path('users/<int:pk>/', views_user.UserDetailView.as_view(), name='user_detail'),
    path('users/<int:pk>/password/', views_user.PasswordView.as_view(), name='user_password'),
    
    path('stores/', views_store.StoreListView.as_view(), name='store_list'),
    path('stores/<int:pk>/', views_store.StoreDetailView.as_view(), name='store_detail'),
]