from django.urls import path
from users import views
from django.contrib.auth.views import LoginView

urlpatterns = [
    path("login/", LoginView.as_view(template_name="login.html"), name="login"),
    path("logout/", views.logout, name="logout"),
]
