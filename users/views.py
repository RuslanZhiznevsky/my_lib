from django.shortcuts import redirect
from django.contrib.auth import logout


def logout_view(request, redirect_to="your_all_books"):
    logout(request)
    return redirect(redirect_to)
