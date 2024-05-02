from django.urls import path
from library import views


urlpatterns = [
    path("", views.all_books, name="your_all_books"),

    path("new_book/", views.new_book, name="new_book"),
    path("book/<str:book_title> by <str:author>/", views.book, name="your_book"),

    path("new_category/", views.new_category, name="new_category"),
    path("categories_order/", views.categories_order, name="categories_order"),

    path("users/", views.users_list, name="users_list"),
    path("users/<str:username>/", views.all_books, name="someones_all_books"),
    path("users/<str:username>/<str:category>/", views.category, name="someones_category"),
    path("users/<str:username>/book/<str:book_title> by <str:author>/", views.book, name="someones_book"),

    path("<str:category>/", views.category, name="your_category"),
]
