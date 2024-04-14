from django.contrib import admin
from .models import Book, BookCategory, LibraryGroup


# Register your models here.
admin.site.register(Book)
admin.site.register(BookCategory)
admin.site.register(LibraryGroup)
