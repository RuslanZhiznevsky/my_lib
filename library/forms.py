from django.forms import ModelForm
from library.models import Book, BookCategory


class NewBookForm(ModelForm):
    class Meta:
        model = Book
        fields = ["title", "author", "category", "file",
                  "started", "finished", "rating", "comment"]

        exclude = ["user"]


class NewCategoryForm(ModelForm):
    class Meta:
        model = BookCategory
        fields = ["category_name"]
