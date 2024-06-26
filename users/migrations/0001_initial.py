# Generated by Django 4.2.6 on 2024-04-14 17:27

from django.conf import settings
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import users.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('username', models.CharField(help_text='unique username', max_length=20, primary_key=True, serialize=False, unique=True, validators=[django.core.validators.MinLengthValidator(3)], verbose_name='username')),
                ('email', models.EmailField(help_text='active email for connection with this account', max_length=255, unique=True, verbose_name='email')),
                ('profile_picture', models.ImageField(blank=True, default=None, help_text='profile picture', max_length=255, null=True, upload_to=users.models.User.get_profile_picture_upload_path, verbose_name='profile picture')),
                ('to_show', models.BooleanField(default=True, help_text="if this flag is set to False user won't be listed in any public listings", verbose_name='to show')),
                ('is_active', models.BooleanField(default=True)),
                ('is_staff', models.BooleanField(default=False)),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.group', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.permission', verbose_name='user permissions')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='UserFollowing',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('who_follows', models.ForeignKey(help_text='user that is following some other user', on_delete=django.db.models.deletion.CASCADE, related_name='following', to=settings.AUTH_USER_MODEL, verbose_name='user-follower')),
                ('whom_follows', models.ForeignKey(help_text='user that is being followed by some other user', on_delete=django.db.models.deletion.CASCADE, related_name='followers', related_query_name='follower', to=settings.AUTH_USER_MODEL, verbose_name='followed user')),
            ],
        ),
        migrations.AddConstraint(
            model_name='userfollowing',
            constraint=models.CheckConstraint(check=models.Q(('who_follows', models.F('whom_follows')), _negated=True), name='users_userfollowing_self_following'),
        ),
        migrations.AlterUniqueTogether(
            name='userfollowing',
            unique_together={('who_follows', 'whom_follows')},
        ),
    ]
