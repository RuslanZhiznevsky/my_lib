from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import Http404

from library.models import BookCategory, Book
from library.forms import BookForm, CategoryForm

from users.models import User

from collections import OrderedDict
import os
import shutil


def _move_book_files(book: Book, to_move_file=True, to_move_cover=True):
    '''Moves book file and cover file to the directory
    according to the new title or author.

    Old files left untouched. You might want to delete them.
    '''
    if book.file and to_move_file:
        storage = book.file.storage
        new_file_path = Book._get_book_assosiated_file_upload_path(
            book,
            book.file.name.split("/")[-1]
        )
        # create copy of the file at the new path
        storage.save(new_file_path, book.file.file)
        book.file.name = new_file_path

    if book.cover and to_move_cover:
        storage = book.cover.storage
        new_cover_path = Book._get_book_assosiated_file_upload_path(
            book,
            book.cover.name.split("/")[-1]
        )
        print(new_cover_path)
        storage.save(new_cover_path, book.cover.file)
        book.cover.name = new_cover_path


def _sort_user_books_by_categories(user):
    books = user.books.all()
    books_by_categories = OrderedDict()

    # make all the possible for this user categories empty lists
    # so when there is no books in some category(ies) you can still access this
    # category dict key in category() view
    category_objs = BookCategory.objects.filter(user=user).order_by("position")
    for category in [category_obj.category_name for category_obj in category_objs]:
        books_by_categories[category] = []

    for book in books:
        category_obj = book.category
        books_by_categories[category_obj.category_name] += [book]

    return books_by_categories


def _get_books_by_categories_and_viewed_user(request, username):
    if username is None:
        books_by_categories = _sort_user_books_by_categories(request.user)
        viewed_user = None
    else:
        viewed_user = get_object_or_404(User, username=username)
        books_by_categories = _sort_user_books_by_categories(viewed_user)

    return books_by_categories, viewed_user


def _raise_404_if_private(user: User):
    if user.is_private is False:  # user has private account
        raise Http404


@login_required
def all_books(request, username=None):
    books_by_categories, viewed_user = _get_books_by_categories_and_viewed_user(request, username)

    if viewed_user:
        _raise_404_if_private(viewed_user)

    context = {
        "user": request.user,

        "viewed_user": viewed_user,
        "books_by_categories": books_by_categories,
    }

    return render(request, "all_books.html", context=context)


@login_required
def category(request, category, username=None):
    books_by_categories, viewed_user = _get_books_by_categories_and_viewed_user(request, username)
    if viewed_user:
        _raise_404_if_private(viewed_user)

    try:
        books = books_by_categories[category]
    except KeyError:
        raise Http404

    context = {
        "user": request.user,

        "viewed_user": viewed_user,
        "category": category,
        "books": books,
    }

    return render(request, "category.html", context=context)


@login_required
def categories_order(request):
    if request.method == "POST":
        positions = {}
        category_names_from_selects = []
        categoires = request.user.book_categories.all()

        for key, value in request.POST.items():
            if key.startswith("bookcategory_select_"):
                # if so, value is a category name
                category_names_from_selects.append(value)
                if category_names_from_selects.count(value) != 1:
                    raise ValueError(f"category '{value}' was assign multiple positions")

                book_category = categoires.get(category_name=value)
                position = int(key.split("bookcategory_select_")[1])
                positions[book_category] = position

        # set positions of categories according to provided POST
        BookCategory.set_positions(positions)

        return redirect("your_all_books")

    if request.method == "GET":
        categories = _sort_user_books_by_categories(user=request.user).keys()

    context = {
        "user": request.user,
        "categories": categories,
    }

    return render(request, "categories_order.html", context=context)


@login_required
def book(request, book_title, author, username=None):
    if username is None:
        book = get_object_or_404(Book, user=request.user, title=book_title, author=author)
        viewed_user = None
    else:
        viewed_user = get_object_or_404(User, username=username)
        book = get_object_or_404(Book, user=viewed_user, title=book_title, author=author)

    if viewed_user:
        _raise_404_if_private(viewed_user)

    if request.method == "GET":
        form = BookForm(instance=book)

    if request.method == "POST":
        populated_filefields = book.get_populated_filefields()
        fields_files_of_which_to_move = [field.field.name for field in populated_filefields]
        print(f"{fields_files_of_which_to_move}")
        old_file_paths = {}

        for filefield in populated_filefields:
            old_file_paths[filefield.field.name] = filefield.path

        old_dirs = set(["/".join(file_path.split("/")[:-1]) for file_path in old_file_paths.values()])
        print(f"old_file_paths: {old_file_paths}")
        print(f"old_dirs: {old_dirs}")

        form = BookForm(request.POST, request.FILES, instance=book)
        if form.is_valid():
            updated_book = form.save(commit=False)
            for filefield in populated_filefields:
                field_name = filefield.field.name
                if field_name in form.changed_data:
                    print(f"{field_name} in changed_data.")
                    os.remove(old_file_paths[field_name])
                    fields_files_of_which_to_move.remove(field_name)

            if "title" in form.changed_data or "author" in form.changed_data:
                print(f"changed title or author. Updating file paths...")
                print(f"{fields_files_of_which_to_move}")
                book.update_book_assosiated_file_paths(fields_files_of_which_to_move)
                for old_dir in old_dirs:
                    print(f"deleting {old_dir}")
                    shutil.rmtree(old_dir)

            updated_book.save()
            return redirect("your_book", updated_book.title, updated_book.author)

    context = {
        "user": request.user,
        "viewed_user": viewed_user,
        "book": book,
        "form": form,
    }

    return render(request, "book.html", context=context)


# TODO if form is NOT valid
# TODO redirect back
@login_required
def new_book(request):
    if request.method == "POST":
        form = BookForm(request.POST, request.FILES)
        if form.is_valid():
            new_book = form.save(commit=False)

            if new_book.author == "":
                new_book.author = "unset"

            new_book.user = request.user
            new_book.clean()
            new_book.save()

            return redirect("your_all_books")
        else:
            pass

    if request.method == "GET":
        category_name = request.GET.get("category", None)
        category_obj = get_object_or_404(
            BookCategory,
            user=request.user,
            category_name=category_name,
        )

        initial = dict(request.GET)
        initial = {key: value[0] for key, value in initial.items()} # value = ['string'], so value[0] == 'string'
        initial.update({"category": category_obj}) # category must be BookCategory object

        # delete anything that was provided inside 'file' & 'cover' GET parameter
        # for security
        try:
            del initial["file"]
        except KeyError:
            pass

        try:
            del initial["cover"]
        except KeyError:
            pass

        form = BookForm(initial=initial)

    context = {
        "new_book_form": form,
        "errors": form.errors,
    }

    return render(request, "new_book.html", context=context)


# TODO if form is NOT valid
# TODO redirect back
@login_required
def new_category(request):
    if request.method == "POST":
        new_category_form = CategoryForm(request.POST)
        if new_category_form.is_valid():
            new_category_model_obj = new_category_form.save(commit=False)

            new_category_model_obj.user = request.user
            new_category_model_obj.clean()
            new_category_model_obj.save()
        else:
            pass

    if request.method == "GET":
        new_category_form = CategoryForm()

    context = {
        "new_category_form": new_category_form,
        "errors": new_category_form.errors,
    }

    return render(request, "new_category.html", context=context)


def users_list(request):
    return render(request, "users_list.html")
