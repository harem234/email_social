from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext_lazy as _

from .forms import CustomUserChangeForm, CustomUserCreationForm, CustomPasswordChangeForm
from .models import EmailUser


# CustomUserAdmin for custom user model subclass from AbstractUser
# https://docs.djangoproject.com/en/2.2/topics/auth/customizing/#custom-users-and-django-contrib-admin
class CustomUserAdmin(UserAdmin):
    model = EmailUser

    form = CustomUserChangeForm
    add_form = CustomUserCreationForm

    change_password_form = CustomPasswordChangeForm

    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        (_('Personal info'), {'fields': ('first_name', 'last_name',)}),
        (_('Permissions'), {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
        }),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
        (_('other'), {'fields': ('username',)}),
    )

    #
    # custom_add_fieldsets = UserAdmin.add_fieldsets
    # custom_add_fieldsets[0][1]['fields'] = ('email', 'password1', 'password2')
    # add_fieldsets = custom_add_fieldsets + (
    #     (_('extended'), {'fields': ('site', 'is_email_verified',)}),
    # )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2'),
        }),
    )

    list_display = ('email', 'username', 'first_name', 'last_name', 'is_staff', 'site', 'site_id',)
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'groups')
    search_fields = ('email', 'username', 'first_name', 'last_name',)
    ordering = ('email',)
    filter_horizontal = ('groups', 'user_permissions',)


admin.site.register(EmailUser, CustomUserAdmin)
