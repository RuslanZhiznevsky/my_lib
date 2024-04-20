from django.db import models, transaction
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
        "BookCategory",
        on_delete=models.CASCADE,
        verbose_name="category",
    )

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
        # Should only occure when using NewBookForm,
        # because user field has blank and null = False 
        except User.DoesNotExist:
            pass

        return super().clean()

    class Meta:
        constraints = [
            models.CheckConstraint(
                check=~models.Q(started__gt=models.F("finished")),
                name="%(app_label)s_%(class)s_finished_before_started"
            ),
            models.UniqueConstraint(
                fields=["user", "title", "author"],
                name="%(app_label)s_%(class)s_user_title_author_unique",
            )
        ]


# TODO: add tests
class BookCategory(models.Model):
    def _last_position():
        field = "position"
        _dict = BookCategory.objects.aggregate(models.Max(field, default=0))

        return _dict[f"{field}__max"] + 1

    def swap_position(self, new_position: int):
        with transaction.atomic():
            if self.position == new_position:
                # no need to swap with itself
                return
            else:
                book_category_to_swap_with = BookCategory.objects.get(position=new_position)

                book_category_to_swap_with.position = self.position
                self.position = new_position

                self.save()
                book_category_to_swap_with.save()

    @staticmethod
    def set_positions(categories_positions: dict):
        '''Sets new positions to the provided BookCategory objects

        !!!Give users a way to only call this method on THEIR categories!!!

        positions: Dict[BookCategory, int]

        raises django.core.exceptions.ValidationErro
        if there are 2 BookCategory objects with the same user and position'''
        with transaction.atomic():
            for category, position in categories_positions.items():
                category.position = position
                category.save()

            # check if UniqueConstraint for user and position is violated
            # if it is violated rollback will be performed and positions
            # of the categories will return to the previous state
            for category in categories_positions:
                category.validate_constraints()

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name="user",
        help_text="user, to whom add category",
        on_delete=models.CASCADE,
        related_name="book_categories",
        related_query_name="book_category",
    )
    category_name = models.CharField(
        verbose_name="category_name",
        help_text="category of the book(fantasy, horror, etc.)",
        max_length=20,
        blank=False,
        # don't set True if blank=True
        null=False,
    )
    position = models.PositiveIntegerField(
        default=_last_position,
        verbose_name="position",
        help_text="position in the list of categories",
        blank=False,
        null=False,
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                name="%(app_label)s_%(class)s_user_and_category_unique",
                fields=["user", "category_name"]
            ),
            models.UniqueConstraint(
                fields=["user", "position"],
                name="%(app_label)s_%(class)s_user_and_postion_unique",
            )
        ]

    def __str__(self):
        return f"{self.user}: '{self.category_name}' category[{self.position}]"


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
