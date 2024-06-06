from django.forms import ModelForm
from library.models import Book, BookCategory


class BookForm(ModelForm):
    class Meta:
        model = Book
        fields = ["title", "author", "category", "file", "cover",
                  "started", "finished", "rating", "comment"]

        exclude = ["user"]

    def clean(self):
        if self.cleaned_data["author"] == "":
            self.cleaned_data["author"] = "unset"

        return super().clean()


class CategoryForm(ModelForm):
    class Meta:
        model = BookCategory
        fields = ["category_name"]
