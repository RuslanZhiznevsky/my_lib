from django.shortcuts import render
from django.contrib.auth.decorators import login_required

from library.models import UserCategory, Book
from library.forms import NewBookForm, NewCategoryForm

from users.models import User


def _sort_user_books_by_categories(user):
    books = user.books.all()
    books_by_categories = {}

    # make all the possible for this user categories empty lists
    # so when there is no books in some category(ies) you can still access this
    # category in category(request, category, username=None) view
    category_objs = UserCategory.objects.filter(user=user)
    for category in [category_obj.category_name for category_obj in category_objs]:
        books_by_categories[category] = []

    for book in books:
        category_obj = book.category
        books_by_categories[category_obj.category_name] += [book]

    return books_by_categories


@login_required  # login_url="/login/")
def all_books(request, username=None):
    if username is None:
        books_by_categories = _sort_user_books_by_categories(request.user)
        viewed_user = None
    else:
        viewed_user = User.objects.get(username=username)
        books_by_categories = _sort_user_books_by_categories(viewed_user)

    context = {
        "user": request.user,

        "viewed_user": viewed_user,
        "books_by_categories": books_by_categories,
    }

    return render(request, "all_books.html", context=context)


@login_required
def category(request, category, username=None):
    if username is None:
        books = _sort_user_books_by_categories(request.user)
        viewed_user = None
    else:
        viewed_user = User.objects.get(username=username)
        books = _sort_user_books_by_categories(viewed_user)[category]

    context = {
        "user": request.user,

        "viewed_user": viewed_user,
        "category": category,
        "books": books,
    }

    return render(request, "category.html", context=context)


@login_required
def book(request, book_title, username=None):
    if username is None:
        book = request.user.books.get(title=book_title)
        viewed_user = None
    else:
        viewed_user = User.objects.get(username=username)
        book = viewed_user.books.get(title=book_title)

    context = {
        "user": request.user,

        "viewed_user": viewed_user,
        "book": book,
    }

    return render(request, "book.html", context=context)


# TODO if form is NOT valid
# TODO redirect back
@login_required
def new_book(request):
    if request.method == "POST":
        new_book_form = NewBookForm(request.POST)
        if new_book_form.is_valid():
            data_to_create_new_book = new_book_form.cleaned_data
            data_to_create_new_book.update({"user": request.user})

            Book.objects.create(**data_to_create_new_book)

            # redirect back
        else:
            pass

    if request.method == "GET":
        new_book_form = NewBookForm()

    context = {
        "new_book_form": new_book_form,
        "errors": new_book_form.errors,
    }

    return render(request, "new_book.html", context=context)


# TODO if form is NOT valid
# TODO redirect back
@login_required
def new_category(request):
    if request.method == "POST":
        new_category_form = NewCategoryForm(request.POST)
        if new_category_form.is_valid():
            new_category_model_obj = new_category_form.save(commit=False)

            new_category_model_obj.user = request.user
            new_category_model_obj.save()
        else:
            pass

    if request.method == "GET":
        new_category_form = NewCategoryForm()

    context = {
        "new_category_form": new_category_form,
        "errors": new_category_form.errors,
    }

    return render(request, "new_category.html", context=context)


def users_list(request):
    return render(request, "users_list.html")
