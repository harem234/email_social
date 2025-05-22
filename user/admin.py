from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import get_user_model

from .forms import CustomUserChangeForm, CustomAdminUserCreationForm, CustomAdminPasswordChangeForm

User_model = get_user_model()

class CustomUserAdmin(UserAdmin):
    list_display = ("email", "is_staff", "is_active",)
    list_filter = ("email", "is_staff", "is_active",)
    fieldsets = (
        (None, {"fields": ("email", "password")}),
        ("Permissions", {"fields": ("is_staff", "is_active", "groups", "user_permissions")}),
    )
    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": (
                "email", "password1", "password2", "is_staff",
                "is_active", "groups", "user_permissions"
            )}
        ),
    )
    form = CustomUserChangeForm
    add_form = CustomAdminUserCreationForm
    change_password_form = CustomAdminPasswordChangeForm
    search_fields = ("email",)
    ordering = ("email",)

admin.site.register(User_model, CustomUserAdmin)