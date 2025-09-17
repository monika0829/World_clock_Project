from django.urls import path
from accounts import views

urlpatterns = [
    path("", views.login_view, name="login"),       # ✅ root → login
    path("register/", views.register_view, name="register"),
    path("home/", views.home_view, name="home"),
    path("clock/", views.clock_view, name="clock"),
    path("logout/", views.logout_view, name="logout"),
]

