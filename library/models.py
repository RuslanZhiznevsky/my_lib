from django.db import models
from django.core.validators import (
    MaxValueValidator,
    MinValueValidator,
)
from django.core.exceptions import ValidationError
from django.conf import settings

from users.models import User

import datetime

DEFAULT_BOOK_CATEGORIES = ["to-read", "reading", "finished"]


class Book(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name="user",
        help_text="user who has this book in their library",
        on_delete=models.CASCADE,
        related_name="books",
        related_query_name="book",
        null=False,
        blank=False,
    )

    title = models.CharField(
        verbose_name="title",
        help_text="title of the book",
        max_length=60,
        blank=True,
        # don't set True if blank=True
        null=False,
        unique=False,
    )

    author = models.CharField(
        verbose_name="author",
        help_text="author of the book",
        max_length=60,
        blank=True,
        # don't set True if blank=True
        null=False,
        unique=False,
    )

    started = models.DateField(
        verbose_name="started",
        help_text="date when started reading",
        # auto_now_add=True,
        default=datetime.date.today,
        editable=True,
        blank=True,
        null=True,
    )

    finished = models.DateField(
        verbose_name="finished",
        help_text="date when finished reading",
        editable=True,
        blank=True,
        null=True,
        default=None,
    )

    rating = models.PositiveIntegerField(
        verbose_name="rating",
        help_text="book rating from 1 to 10",
        blank=True,
        null=True,
        default=None,
        validators=[MaxValueValidator(10), MinValueValidator(1)],
    )

    comment = models.TextField(
        verbose_name="comment",
        help_text="comment on this book. Is it bad? Good?",
        blank=True,
    )

    # TODO on_delete change category to some default
    category = models.ForeignKey(
        "UserCategory",
        on_delete=models.CASCADE,
        verbose_name="category",

    )

    # TODO constraint or some sort for unique combo of username + title
    # TODO change filepath when changed inside view
    def _get_bookfile_upload_path(instance, filename):
        return f"books/{instance.user}/{instance.author}_{instance.title}/{filename}"
    file = models.FileField(
        verbose_name="book file",
        help_text="book file to upload",
        upload_to=_get_bookfile_upload_path,
        blank=True,
        null=True,
        default=None,
    )

    def _get_coverfile_upload_path(instance, filename):
        return f"books/{instance.user}/{instance.author}_{instance.title}/{filename}"
    # TODO change filepath when updated inside view
    cover = models.ImageField(
        verbose_name="cover image",
        help_text="image of the cover of the book",
        upload_to=_get_coverfile_upload_path,
        blank=True,
        null=True,
        default=None,
    )

    def __str__(self):
        return f"{self.user}:{self.title} by {self.author}"

    def clean(self):
        try:
            if self.category.user != self.user:
                raise ValidationError("Another user's category was assigned to this book")

        # for NewBook form which gets no user object:
        except User.DoesNotExist:
            pass

        return super().clean()

    class Meta:
        constraints = [
            models.CheckConstraint(
                check=~models.Q(started__gt=models.F("finished")),
                name="%(app_label)s_%(class)s_finished_before_started"
            ),
        ]


# TODO: add tests
class UserCategory(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name="user",
        help_text="user, to whom add category",
        on_delete=models.CASCADE,
        related_name="user_categories",
        related_query_name="user_category",
    )
    category_name = models.CharField(
        verbose_name="category",
        help_text="category of the book(fantasy, horror, etc.)",
        max_length=20,
        blank=False,
        # don't set True if blank=True
        null=False,
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                name="%(app_label)s_%(class)s_user_and_category_unique",
                fields=["user", "category_name"]
            )
        ]

    def __str__(self):
        return f"{self.user}: '{self.category_name}' category"


class LibraryGroup(models.Model):
    creator = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name="creator of the group",
        help_text="person who created the group",
        on_delete=models.SET("DELETED"),
        related_name="created_groups",
        related_query_name="created_group",
        null=False,
    )

    name = models.CharField(
        verbose_name="group name",
        help_text="group name",
        max_length=40,
        blank=False,
        # don't set True if blank=True
        null=False,
        unique=True,
        primary_key=True,
    )
    # users retreived from user.User
    users = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        verbose_name="group members",
        help_text="users who are part of this group",
        related_name="library_groups",
        related_query_name="library_group",
        blank=False,
        symmetrical=False,
    )

    def __str__(self):
        return f"{self.name}"
