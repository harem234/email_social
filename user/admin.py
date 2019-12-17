from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext_lazy as _

from .forms import CustomUserChangeForm, CustomUserCreationForm
from .models import EmailUser


# CustomUserAdmin for custom user model subclass from AbstractUser
# https://docs.djangoproject.com/en/2.2/topics/auth/customizing/#custom-users-and-django-contrib-admin
class CustomUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        (_('extended'), {'fields': ('site', 'isEmailVerified',)}),
    )

    #
    custom_add_fieldsets = UserAdmin.add_fieldsets
    custom_add_fieldsets[0][1]['fields'] = ('email', 'password1', 'password2')
    add_fieldsets = custom_add_fieldsets + (
        (_('extended'), {'fields': ('site', 'isEmailVerified',)}),
    )
    form = CustomUserChangeForm
    add_form = CustomUserCreationForm
    model = EmailUser
    list_display = UserAdmin.list_display + ('email', 'site', 'site_id',)


admin.site.register(EmailUser, CustomUserAdmin)
