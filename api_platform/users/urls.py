"""users/urls.py"""

from django.urls import path

from users.views import RegisterView, LoginView

urlpatterns = [
    path("register/", RegisterView.as_view(), name="user-register"),
    path("login/", LoginView.as_view(), name="user-login"),
]
