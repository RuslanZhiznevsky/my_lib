from django.conf import settings
from django.db import models
from django.core.validators import MinLengthValidator
from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin
)


class UserManager(BaseUserManager):
    def create_user(self, username, email, password=None, profile_picture=None):
        if not email:
            raise ValueError("Users must have an email")

        user = self.model(
            username=username,
            email=self.normalize_email(email),
            profile_picture=profile_picture,
            to_show=True,
            is_active=True,
            is_staff=False,
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create(self, *args, **kwargs):
        return self.create_user(*args, **kwargs)

    def create_superuser(self, username, email, password=None):
        user = self.create_user(
            username=username,
            email=email,
            password=password,
        )
        user.is_superuser = True
        user.is_active = True
        user.is_staff = True
        user.save(using=self._db)
        return user


class User(AbstractBaseUser, PermissionsMixin):
    def get_profile_picture_upload_path(instance, filename):
        return f"profile_pictures/{instance.username}/{filename}"

    username = models.CharField(
        verbose_name="username",
        primary_key=True,
        unique=True,
        blank=False,
        null=False,     # don't set True if blank=True
        max_length=20,
        help_text="unique username",

        validators=[MinLengthValidator(3)],
    )
    email = models.EmailField(
        verbose_name="email",
        help_text="active email for connection with this account",
        max_length=255,
        unique=True,
        blank=False,
        null=False,
    )
    profile_picture = models.ImageField(
        verbose_name="profile picture",
        help_text="profile picture",
        upload_to=get_profile_picture_upload_path,
        max_length=255,
        blank=True,
        null=True,
        default=None,
    )

    # library_groups            from library.models.Book

    # following                 from UserFollowing model
    # followers                 from UserFollowing model

    # books                     from library.Book model
    # extra_book_catagories     from library.models.Book

    to_show = models.BooleanField(
        verbose_name="to show",
        help_text="if this flag is set to False "
                  "user won't be listed in any public listings",
        default=True,
    )

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    # is_superuser              from PermissionsMixin

    USERNAME_FIELD = "username"
    EMAIL_FIELD = "email"
    REQUIRED_FIELDS = ["email"]

    objects = UserManager()

    def __str__(self):
        return self.username


class UserFollowing(models.Model):
    who_follows = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name="user-follower",
        help_text="user that is following some other user",
        related_name="following",
        on_delete=models.CASCADE,
        blank=False,
        null=False,
    )
    whom_follows = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name="followed user",
        help_text="user that is being followed by some other user",
        related_name="followers",
        related_query_name="follower",
        on_delete=models.CASCADE,
        blank=False,
        null=False,
    )

    class Meta:
        unique_together = ("who_follows", "whom_follows")
        constraints = [
            models.CheckConstraint(
                name="%(app_label)s_%(class)s_self_following",
                check=~models.Q(who_follows=models.F("whom_follows")),
            ),
        ]

    def __str__(self):
        return f"{self.who_follows} -> {self.whom_follows}"
