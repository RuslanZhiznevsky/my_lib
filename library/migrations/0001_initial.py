# Generated by Django 4.2.6 on 2024-04-14 17:27

import datetime
import django.core.validators
from django.db import migrations, models
import library.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Book',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(blank=True, help_text='title of the book', max_length=60, verbose_name='title')),
                ('author', models.CharField(blank=True, help_text='author of the book', max_length=60, verbose_name='author')),
                ('started', models.DateField(blank=True, default=datetime.date.today, help_text='date when started reading', null=True, verbose_name='started')),
                ('finished', models.DateField(blank=True, default=None, help_text='date when finished reading', null=True, verbose_name='finished')),
                ('rating', models.PositiveIntegerField(blank=True, default=None, help_text='book rating from 1 to 10', null=True, validators=[django.core.validators.MaxValueValidator(10), django.core.validators.MinValueValidator(1)], verbose_name='rating')),
                ('comment', models.TextField(blank=True, help_text='comment on this book. Is it bad? Good?', verbose_name='comment')),
                ('file', models.FileField(blank=True, default=None, help_text='book file to upload', null=True, upload_to=library.models.Book._get_bookfile_upload_path, verbose_name='book file')),
                ('cover', models.ImageField(blank=True, default=None, help_text='image of the cover of the book', null=True, upload_to=library.models.Book._get_coverfile_upload_path, verbose_name='cover image')),
            ],
        ),
        migrations.CreateModel(
            name='BookCategory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('category_name', models.CharField(help_text='category of the book(fantasy, horror, etc.)', max_length=20, verbose_name='category_name')),
                ('position', models.PositiveIntegerField(default=library.models.BookCategory._last_position, help_text='position in the list of categories', verbose_name='position')),
            ],
        ),
        migrations.CreateModel(
            name='LibraryGroup',
            fields=[
                ('name', models.CharField(help_text='group name', max_length=40, primary_key=True, serialize=False, unique=True, verbose_name='group name')),
            ],
        ),
    ]
