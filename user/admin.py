from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _

from .forms import CustomUserChangeForm, CustomAdminUserCreationForm, CustomAdminPasswordChangeForm

User_model = get_user_model()

class CustomUserAdmin(UserAdmin):

    fieldsets = (
        (None, {"fields": ("email", "password")}),
        (_("Personal info"), {"fields": ("first_name", "last_name", "email")}),
        (
            _("Permissions"),
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
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
                "fields": ("email", "usable_password", "password1", "password2"),
            },
        ),
    )

    form = CustomUserChangeForm
    add_form = CustomAdminUserCreationForm
    change_password_form = CustomAdminPasswordChangeForm

    list_display = ( "email", "first_name", "last_name", "is_staff", "username",)
    list_filter = ("is_staff", "is_superuser", "is_active", "groups")
    search_fields = ( "first_name", "last_name", "email", "username",)
    ordering = ("email",)

admin.site.register(User_model, CustomUserAdmin)