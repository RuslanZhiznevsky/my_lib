# TODO file and cover tests
from django.test import TestCase, override_settings
from utils import ModelTestUtils
from django.db import IntegrityError
from django.utils import timezone
from django.core.files import File
from django.core.exceptions import ValidationError

from users.models import User
from library.models import Book, UserCategory, LibraryGroup

from random import randint

import shutil
import tempfile


MEDIA_ROOT = tempfile.mkdtemp()


@override_settings(MEDIA_ROOT=MEDIA_ROOT)
class BookModelTest(TestCase, ModelTestUtils):
    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(MEDIA_ROOT, ignore_errors=True)  # delete the temp dir
        super().tearDownClass()

    @classmethod
    def add_user(cls, username):
        user = None

        return user

    @classmethod
    def add_books(cls,):
        new = None

        return new

    @classmethod
    def setUpTestData(cls):
        cls.default_obj = None
        cls.unsaved_obj = None
        cls.max_lengths = {
            "title": 60,
            "author": 60,
        }

    def test_user__verbose_name(self):
        self.field_meta_attrib_eq("user")

    def test_user__help_text(self):
        self.field_meta_attrib_eq("user who has this book in their library")

    def test_user__related_name(self):
        self.field_meta_attrib_eq("books")

    def test_user__related_query_name(self):
        self.field_meta_attrib_eq("book")

    def test_title__verbose_name(self):
        self.field_meta_attrib_eq("title")

    def test_title__help_text(self):
        self.field_meta_attrib_eq("title of the book")

    def test_author__verbose_name(self):
        self.field_meta_attrib_eq("author")

    def test_author__help_text(self):
        self.field_meta_attrib_eq("author of the book")

    def test_started__verbose_name(self):
        self.field_meta_attrib_eq("started")

    def test_started__help_text(self):
        self.field_meta_attrib_eq("date when started reading")

    def test_finished__verbose_name(self):
        self.field_meta_attrib_eq("finished")

    def test_finished__help_text(self):
        self.field_meta_attrib_eq("date when finished reading")

    def test_rating__verbose_name(self):
        self.field_meta_attrib_eq("rating")

    def test_rating__help_text(self):
        self.field_meta_attrib_eq("book rating from 1 to 10")

    def test_comment__verbose_name(self):
        self.field_meta_attrib_eq("comment")

    def test_comment__help_text(self):
        self.field_meta_attrib_eq("comment on this book. Is it bad? Good?")

    def test_category_name__verbose_name(self):
        self.field_meta_attrib_eq("category_name")

    def test_category_name__help_text(self):
        self.field_meta_attrib_eq("category of this book(fantasy, horror, etc.)")

    def test_rating_is_zero(self):
        with self.assertRaises(ValidationError):
            self.add_books(1, user=self.add_user("bookhater"), rating=0)

    def test_rating_bigger_than_ten(self):
        with self.assertRaises(ValidationError):
            self.add_books(1, user=self.add_user("booklover"), rating=11)

    def test_cover_file_upload_path(self):
        user = self.add_user("covertester")
        coverfile = File(open("library/tests/media/simple_book_cover.jpg", "rb"))
        coverfile.name = "test.jpg"

        book = self.add_books(1, user=user, cover=coverfile)[0]

        self.assertEqual(
            f"{MEDIA_ROOT}/books/{book.user}/{book.author}_{book.title}/test.jpg",
            book.cover.path,
        )

    def test_bookfile_upload_path(self):
        user = self.add_user(username="bookfiletester")
        bookfile = File(open("library/tests/media/epubtestfile.epub", "rb"))
        bookfile.name = "epubtestfile.epub"

        book = self.add_books(1, user=user, file=bookfile)[0]

        self.assertEqual(
            f"{MEDIA_ROOT}/books/{book.user}/{book.author}_{book.title}/epubtestfile.epub",
            book.file.path,
        )

    # logic tests:

# ------------------------------UserCategory----------------------------------


class UserCategoryTest(TestCase, ModelTestUtils):
    pass


# ------------------------------LibraryGroup----------------------------------


class LibraryGroupTest(TestCase, ModelTestUtils):
    @staticmethod
    def add_user(username):
        user = User.objects.create_user(
            username=username,
            email=f"user{username}@gmail.com",
            password="password1"
        )

        return user

    @classmethod
    def setUpTestData(cls):
        default_obj = LibraryGroup.objects.create(
            creator=cls.add_user("user1"),
            name="Luchik read"
        )

        default_obj.users.add(cls.add_user("user2"))
        default_obj.users.add(cls.add_user("user3"))

        cls.default_obj = default_obj

    def test_creator__verbose_name(self):
        self.field_meta_attrib_eq("creator of the group")

    def test_creator__help_text(self):
        self.field_meta_attrib_eq("person who created the group")

    def test_creator__related_name(self):
        self.field_meta_attrib_eq("created_groups")

    def test_creator__related_query_name(self):
        self.field_meta_attrib_eq("created_group")

    def test_name__verbose_name(self):
        self.field_meta_attrib_eq("group name")

    def test_name__help_text(self):
        self.field_meta_attrib_eq("group name")

    def test_longest_name(self):
        try:
            LibraryGroup.objects.create(
                creator=self.add_user("longest"),
                name=40*"n"
            ).full_clean()
        except ValidationError:
            self.fail("LibraryGroup.name with length 40 must be valid but it is not")

    def test_name_too_long(self):
        with self.assertRaises(ValidationError):
            LibraryGroup.objects.create(
                creator=self.add_user("long"),
                name=41*"n"
            ).full_clean()

    def test_users__verbose_name(self):
        self.field_meta_attrib_eq("group members")

    def test_users__help_text(self):
        self.field_meta_attrib_eq("users who are part of this group")

    def test_users__related_name(self):
        self.field_meta_attrib_eq("library_groups")

    def test_users__related_query_name(self):
        self.field_meta_attrib_eq("library_group")

    # logic tests:

    def test_user_can_create_many_groups(self):
        user = self.add_user("manygroups")
        try:
            LibraryGroup.objects.create(creator=user, name="new1")
            LibraryGroup.objects.create(creator=user, name="new2")
        except Exception as e:
            self.fail("User must be able to create many groups but can't. "
                      f"Exception raised: {e.__class__}. {e}")

    def test_not_unique_group_name(self):
        user1 = self.add_user("uuser1")
        user2 = self.add_user("uuser2")
        group_name = "samegropunmae"

        with self.assertRaises(IntegrityError):
            LibraryGroup.objects.create(creator=user1, name=group_name)
            LibraryGroup.objects.create(creator=user2, name=group_name)

    def test_not_unique_group_name_by_the_same_user(self):
        user = self.add_user("uuuser")
        group_name = "samegroupbysameuser"

        with self.assertRaises(IntegrityError):
            LibraryGroup.objects.create(creator=user, name=group_name)
            LibraryGroup.objects.create(creator=user, name=group_name)
