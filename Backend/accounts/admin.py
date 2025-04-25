from django.contrib import admin
from accounts.models import CustomUser
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext_lazy as _
class CustomUserAdmin(UserAdmin):
    model = CustomUser
    fieldsets = (
        (None, {"fields": ("username", "password")}),
        (_("Personal info"), {"fields": ("first_name", "last_name", "email",)}),
        (
            _("Permissions"),
            {
                "fields": (
                    "is_active",
                    "is_staff",
                ),
            },
        ),
        (_("Important dates"), {"fields": ("last_login", "date_joined")}),
    )
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("username","role", "usable_password", "password1", "password2"),
            },
        ),
    )
    list_display = UserAdmin.list_display 
    list_filter = ('is_active','is_staff','is_superuser')
    search_fields = UserAdmin.search_fields 
    ordering = UserAdmin.ordering 
    filter_horizontal = []
    
admin.site.register(CustomUser, CustomUserAdmin)