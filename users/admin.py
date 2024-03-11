from django.contrib import admin
from django.forms import ModelForm
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User


# Register your models here.
class UserCreationForm(ModelForm):
    class Meta:
        model = User
        fields = "__all__"


class UserChangeForm(ModelForm):
    class Meta:
        model = User
        fields = "__all__"


class UserAdmin(BaseUserAdmin):
    form = UserChangeForm
    add_form = UserCreationForm

    list_display = ["username", "email", "profile_picture", "is_active", "is_staff", "is_superuser"]

    list_display = ["username", "email", "profile_picture", "is_active", "is_staff", "is_superuser"]
    list_filter = ["is_superuser"]
    fieldsets = [
        (None, {"fields": ["username", "email", "password", "profile_picture"]}),
        ("Permissions", {"fields": ["is_superuser", "is_active", "is_staff"]}),
    ]

    add_fieldsets = [
        (
            None,
            {
                "classes": ["wide"],
                "fields": ["username", "email", "profile_picture", "is_active", "is_staff", "is_superuser"],

            },
        ),
    ]


admin.site.register(User, UserAdmin)
