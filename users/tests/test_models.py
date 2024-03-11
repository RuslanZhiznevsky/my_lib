from django.test import TestCase
from users.models import User, UserFollowing

from django.db import IntegrityError
from django.core.exceptions import ValidationError

from utils import ModelTestUtils

DEFAULT_UO_USERNAME = "Test"


def create_user(
    username="Correct",
    email="correct@gmail.com",
    password="correctpassword1",
):
    uo = User.objects.create_user(
        username=username,
        email=email,
        password=password,
    )

    return uo


class UserModelTest(TestCase, ModelTestUtils):
    @classmethod
    def setUpTestData(cls):
        User.objects.create_user(
            username=DEFAULT_UO_USERNAME,
            email="someemail@gmail.com",
            password="password1",
        )
        cls.default_obj = User.objects.get(pk=DEFAULT_UO_USERNAME)

    def test_username__verbose_name(self):
        self.field_meta_attrib_eq("username")

    def test_username__help_text(self):
        self.field_meta_attrib_eq("unique username")

    def test_user_model_username_too_long(self):
        uo = create_user(
            username=21*"o",
        )
        with self.assertRaises(ValidationError):
            uo.full_clean()

    def test_user_model_username_too_short(self):
        uo = create_user(username=2*"o")
        with self.assertRaises(ValidationError):
            uo.full_clean()

    def test_user_model_username_longest(self):
        uo = create_user(username=20*"o")
        try:
            uo.full_clean()
        except ValidationError:
            self.fail("This shouldn't raise exception cause username length = "
                      "max_length")

    def test_user_model_username_shortest(self):
        uo = create_user(username=3*"o")
        try:
            uo.full_clean()
        except ValidationError:
            self.fail("Shouldn't raise exception 'cause username length = "
                      "shortest")

    def test_email__verbose_name(self):
        self.field_meta_attrib_eq("email")

    def test_email__help_text(self):
        self.field_meta_attrib_eq("active email for connection with this account")

    def test_profile_picture__verbose_name(self):
        self.field_meta_attrib_eq("profile picture")

    def test_profile_picture__help_text(self):
        self.field_meta_attrib_eq("profile picture")

    def test_user_model_profile_picture_uploads_to_right_place(self):
        pass

    def test_to_show__verbose_name(self):
        self.field_meta_attrib_eq("to show")

    def test_to_show__help_text(self):
        self.field_meta_attrib_eq("if this flag is set to False user won't be listed in any public listings")

    def test_user_model_default_user_has_rigth_admin_permissions(self):
        uo = self.default_obj
        self.assertFalse(uo.is_staff, "Default user must not be staff member")
        self.assertFalse(uo.is_superuser, "Default user must not be superuser")

    def test_user_model_superuser_has_right_admin_permissions(self):
        uo = User.objects.create_superuser(
            "superuser",
            "superuser@gmail.com",
            "superpassword1",
        )
        self.assertTrue(uo.is_staff, "Superuser must be staff member")
        self.assertTrue(uo.is_superuser, "Superuser must be superuser")

    def test_user_model_user_creation_without_email(self):
        with self.assertRaises(ValueError):
            User.objects.create_user(
                email=None,
                username="usernoemail",
                password="password1"
            )


class UserFollowingTest(TestCase, ModelTestUtils):
    user_count = 0

    @classmethod
    def add_users(cls, num):
        new = []
        for num in range(cls.user_count+1, cls.user_count+num+1):
            new.append(User.objects.create_user(
                username=f"user{num}",
                email=f"email{num}@gmail.com",
                password=f"password{num}",
            ))
        cls.user_count += num

        return new

    @classmethod
    def setUpTestData(cls):
        cls.add_users(2)

        default_ufo = UserFollowing.objects.create(
            who_follows=User.objects.get(pk="user1"),
            whom_follows=User.objects.get(pk="user2")
        )
        cls.default_obj = default_ufo

    def test_who_follows__verbose_name(self):
        self.field_meta_attrib_eq("user-follower")

    def test_who_follows__help_text(self):
        self.field_meta_attrib_eq("user that is following some other user")

    def test_who_follows__related_name(self):
        self.field_meta_attrib_eq("following")

    def test_who_follows__related_query_name(self):
        self.field_meta_attrib_eq("following")

    def test_whom_follows__verbose_name(self):
        self.field_meta_attrib_eq("followed user")

    def test_whom_follows__help_text(self):
        self.field_meta_attrib_eq("user that is being followed by some other user")

    def test_whom_follows__related_name(self):
        self.field_meta_attrib_eq("followers")

    def test_whom_follows__related_query_name(self):
        self.field_meta_attrib_eq("follower")

    def test_userfollowing_model_str(self):
        d_o = self.default_obj
        self.assertEqual(
            d_o.__str__(),
            f"{d_o.who_follows} -> {d_o.whom_follows}"
        )

    def test_userfollowing_model_multiple_users_can_follow(self):
        new_users = self.add_users(5)
        for user in new_users[1:]:
            UserFollowing.objects.create(
                who_follows=User.objects.get(pk=user.username),
                whom_follows=User.objects.get(pk="user3")
            )

        self.assertEqual(
            len(User.objects.get(pk="user3").followers.all()),
            4
        )

    def test_userfollowing_model_user_cant_follow_themself(self):
        user = self.add_users(1)[0]
        constraint_name = "users_userfollowing_self_following"
        with self.assertRaisesMessage(IntegrityError, constraint_name):
            UserFollowing.objects.create(
                who_follows=user,
                whom_follows=user,
            )

    def test_userfollowing_model_user_cant_follow_the_same_user_twice(self):
        user1, user2 = self.add_users(2)
        with self.assertRaises(IntegrityError):
            UserFollowing.objects.create(
                who_follows=user1,
                whom_follows=user2,
            )
            UserFollowing.objects.create(
                who_follows=user1,
                whom_follows=user2,
            )
