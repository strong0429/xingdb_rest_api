from django.urls import path

from .views import *

urlpatterns = [
    path('token/', AppTokenView.as_view(), name='app_token'),
    path('sms/', SMSCodeView.as_view(), name='sms_code'),
    path('register/', UserRegisterView.as_view(), name='user_register'),
    path('login/', UserLoginView.as_view(), name='user_login'),
    path('users/<int:pk>/', UserDetailView.as_view(), name='user_detail'),
    path('users/<int:pk>/password/', PasswordView.as_view(), name='user_password'),
    
    path('stores/', StoreListView.as_view(), name='store_list'),
    path('stores/<int:pk>/', StoreDetailView.as_view(), name='store_detail'),
    path('stores/<int:store_id>/sales/', SaleRecordView.as_view(), name='sales'),
    path('stores/<int:store_id>/purchases/', PurchaseView.as_view(), name='purchases'),
    path('stores/<int:store_id>/storages/', StorageView.as_view(), name='storages'),
    
    path('suppliers/', SupplierView.as_view(), name='supplier'),
    path('goods/', GoodsListView.as_view(), name='goods'),
]

