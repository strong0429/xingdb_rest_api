from django.contrib import admin
from .models import User, StoreCategory, PayMode, AppVersion

# Register your models here.
@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('mobile', 'date_joined', 'email')

@admin.register(StoreCategory)
class StoreCategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)

@admin.register(PayMode)
class PayModeAdmin(admin.ModelAdmin):
    list_display = ('mode', 'amount')

@admin.register(AppVersion)
class AppVersionAdmin(admin.ModelAdmin):
    list_display = ('app_name', 'ver_code', 'ver_txt', 'date_pub', 'detail')