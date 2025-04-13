from django.urls import path
from . import views

urlpatterns = [
    path("", views.login_view, name="login"), 
    path("register/", views.register_view, name="register"),
    path("logout/", views.logout_view, name="logout"),
    path("test/", views.test_form, name="test_form"),
    path("profile/", views.profile_view, name="profile"),
    path("profile/edit/", views.profile_edit, name="profile_edit"),
    path("report/", views.report_detail, name="report_detail"),
]
