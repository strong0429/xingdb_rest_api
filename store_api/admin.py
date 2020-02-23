from django.contrib import admin
from .models import XingUser, StoreCategory, PayMode, AppVersion

# Register your models here.
@admin.register(XingUser)
class XingUserAdmin(admin.ModelAdmin):
    list_display = ('username', 'mobile', 'is_staff', 'date_joined', 'email')

@admin.register(StoreCategory)
class StoreCategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)

@admin.register(PayMode)
class PayModeAdmin(admin.ModelAdmin):
    list_display = ('mode', 'amount')

@admin.register(AppVersion)
class AppVersionAdmin(admin.ModelAdmin):
    list_display = ('app_name', 'ver_code', 'ver_txt', 'date_pub', 'detail')