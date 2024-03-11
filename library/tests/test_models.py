# TODO file and cover tests
from django.test import TestCase, override_settings
from utils import ModelTestUtils
from django.db import IntegrityError
from django.utils import timezone
from django.core.files import File
from django.core.exceptions import ValidationError

from users.models import User
from library.models import Book, UserExtraBookCategory, LibraryGroup

from random import randint

import shutil
import tempfile


MEDIA_ROOT = tempfile.mkdtemp()


@override_settings(MEDIA_ROOT=MEDIA_ROOT)
class BookModelTest(TestCase, ModelTestUtils):
    book_count = 0
    user_count = 0

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(MEDIA_ROOT, ignore_errors=True)  # delete the temp dir
        super().tearDownClass()

    @classmethod
    def add_user(cls, username, extra_category=None):
        user = User.objects.create_user(
            username=username,
            email=f"user{cls.user_count}@gmail.com",
            password="password1",
        )
        user.full_clean()
        if extra_category is not None:
            UserExtraBookCategory.objects.create(
                user=user,
                category=extra_category
            )

        cls.user_count += 1
        return user

    @classmethod
    def add_books(cls, num, user, title=None, author=None, started=None,
                  finished=None, rating=None, comment=None, category=None,
                  cover=None, file=None):

        if title is not None:
            title = title
        else:
            title = f"Correct title{num}"

        if author is not None:
            author = author
        else:
            author = f"Correct author{num}"

        if finished is not None:
            finished = finished

        if rating is not None:
            rating = rating
        else:
            rating = 5

        if comment is not None:
            comment = comment
        else:
            comment = "Correct comment"

        if category is not None:
            category = category
        else:
            category = "reading"

        if cover is not None:
            cover = cover

        if file is not None:
            file = file

        new = []
        for num in range(cls.book_count+1, cls.book_count+num+1):
            new_book = Book.objects.create(
                user=user,
                title=title,
                author=author,
                finished=finished,
                rating=rating,
                comment=comment,
                category=category,
                file=file,
                cover=cover,
            )

            if started is not None:
                new_book.started = started

            new_book.full_clean()
            new.append(new_book)

        cls.book_count += num

        return new

    @classmethod
    def setUpTestData(cls):
        user = User.objects.create_user(
            username="user",
            email="email@gmail.com",
            password="password1",
        )
        default_book = cls.add_books(1, user=user)[0]
        cls.default_obj = default_book
        cls.unsaved_obj = Book.objects.create(
            user=cls.add_user("unsaved"),
            title="Stormlight",
            author="Brandon",
        )
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

    def test_category__verbose_name(self):
        self.field_meta_attrib_eq("category")

    def test_category__help_text(self):
        self.field_meta_attrib_eq("category of this book(fantasy, horror, etc.)")

    def test_rating_is_zero(self):
        with self.assertRaises(ValidationError):
            self.add_books(1, user=self.add_user("bookhater"), rating=0)

    def test_rating_bigger_than_ten(self):
        with self.assertRaises(ValidationError):
            self.add_books(1, user=self.add_user("booklover"), rating=11)

    def test_non_existing_category(self):
        with self.assertRaises(ValidationError):
            self.add_books(
                1,
                user=self.add_user("badcategory"),
                category="nonexistent"
            )

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

    def test_finished_before_started(self):
        user = self.add_user("quickfinisher")
        yesterday = (timezone.now() - timezone.timedelta(days=1)).date()
        constraint_name = "library_book_finished_before_started"

        with self.assertRaisesMessage(ValidationError, constraint_name):
            book = self.add_books(1, user=user, finished=yesterday)[0]
            print(book.started, yesterday)

    def test_user_can_have_more_than_one_book(self):
        num = randint(1, 10)

        user = self.add_user("multiple")
        self.add_books(num, user=user)

        self.assertEqual(len(user.books.all()), num)


# ------------------------------UserExtraBookCategory-------------------------


class UserExtraBookCategoryTest(TestCase, ModelTestUtils):
    user_count = 0

    @classmethod
    def add_user(cls, username, extra_category=None):
        user = User.objects.create_user(
            username=username,
            email=f"use{cls.user_count}r@gmail.com",
            password="password1",
        )
        user.full_clean()
        if extra_category is not None:
            UserExtraBookCategory.objects.create(
                user=user,
                category=extra_category
            )

        cls.user_count += 1
        return user

    @classmethod
    def setUpTestData(cls):
        user = cls.add_user("extrabookdefault")
        default_obj = UserExtraBookCategory.objects.create(
            user=user,
            category="default"
        )

        cls.default_obj = default_obj

    def test_user__verbose_name(self):
        self.field_meta_attrib_eq("user")

    def test_user__help_text(self):
        self.field_meta_attrib_eq("user, to whom assign extra book category")

    def test_user__related_name(self):
        self.field_meta_attrib_eq("extra_book_categories")

    def test_user__related_query_name(self):
        self.field_meta_attrib_eq("extra_book_category")

    def test_category__verbose_name(self):
        self.field_meta_attrib_eq("category")

    def test_category__help_text(self):
        self.field_meta_attrib_eq("category of the book(fantasy, horror, etc.)")

    def test_category_too_long(self):
        with self.assertRaises(ValidationError):
            UserExtraBookCategory.objects.create(
                user=self.add_user("longcategory"),
                category=21*"c",
            ).full_clean()

    def test_longest_category(self):
        try:
            UserExtraBookCategory.objects.create(
                user=self.add_user("longestcategory"),
                category=20*"c",
            )
        except ValidationError:
            self.fail("Extra category with length 20 must be valid, but it is not")

    # logic tests:

    def test_user_plus_category_unique(self):
        user = self.add_user("samecategory")
        constraint = "library_userextrabookcategory_user_and_category_unique"

        with self.assertRaises(IntegrityError):
            for i in range(2):
                UserExtraBookCategory.objects.create(
                    user=user,
                    category="samecategory",
                )

    def test_user_can_have_multiple_extra_categories(self):
        user = self.add_user("multiplecategories")

        UserExtraBookCategory.objects.create(user=user, category="first")
        UserExtraBookCategory.objects.create(user=user, category="second")

        self.assertTrue(len(user.extra_book_categories.all()) == 2)

    def test_different_users_have_the_same_category(self):
        user1 = self.add_user("samethinker1")
        user2 = self.add_user("samethinker2")

        category = "samethinking"

        # if there is something wrong exception will be raised
        UserExtraBookCategory.objects.create(user=user1, category=category)
        UserExtraBookCategory.objects.create(user=user2, category=category)

        # but we still have to check to be absolutly sure
        c1 = user1.extra_book_categories.get(category=category).category
        c2 = user2.extra_book_categories.get(category=category).category

        self.assertTrue(c1 == c2)


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
