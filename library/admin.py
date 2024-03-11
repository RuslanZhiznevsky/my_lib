from django.contrib import admin
from .models import Book, UserCategory, LibraryGroup


# Register your models here.
admin.site.register(Book)
admin.site.register(UserCategory)
admin.site.register(LibraryGroup)
