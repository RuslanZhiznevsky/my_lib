from django.urls import path
from library import views


urlpatterns = [
    path("", views.all_books, name="editable_all_books"),

    path("new_book/", views.new_book, name="new_book"),
    path("new_category/", views.new_category, name="new_category"),

    path("book/<str:book_title>/", views.book, name="editable_book"),

    path("users/", views.users_list, name="users_list"),
    path("users/<str:username>/", views.all_books, name="not_editable_all_books"),
    path("users/<str:username>/<str:category>/", views.category, name="not_ditable_category"),
    path("users/<str:username>/book/<str:book_title>/", views.book, name="not_editable_book"),

    path("<str:category>/", views.category, name="editable_category"),
]
