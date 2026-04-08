from django.urls import path

from . import views

urlpatterns = [
    path("", views.dashboard, name="dashboard"),
    path("login-board/", views.login_board, name="login_board"),
    path("login/", views.login_view, name="login"),
    path("admin-login/", views.admin_login, name="admin_login"),
    path("logout/", views.logout_view, name="logout"),
    path("register/", views.register_view, name="register"),

    path("services/add/", views.add_service, name="add_service"),
    path("services/<int:service_id>/", views.service_detail, name="service_detail"),
    path("services/<int:service_id>/edit/", views.edit_service, name="edit_service"),
    path("services/<int:service_id>/delete/", views.delete_service, name="delete_service"),

    path("pages/", views.pages_list, name="pages_list"),
    path("pages/add/", views.add_page, name="add_page"),
    path("pages/<slug:slug>/", views.dynamic_page_view, name="dynamic_page"),

    path("users/", views.user_list, name="user_list"),
    path("users/<int:user_id>/edit/", views.edit_user, name="edit_user"),
]
