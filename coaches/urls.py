from django.urls import path

from . import views


app_name = "coaches"


urlpatterns = [

    path(
        "",
        views.dashboard,
        name="dashboard"
    ),

    path(
        "login/",
        views.coach_login,
        name="login"
    ),

    path(
        "logout/",
        views.coach_logout,
        name="logout"
    ),

    path(
        "management/",
        views.coach_management,
        name="coach_management"
    ),
    path(
        "management/coaches/<int:user_id>/delete/",
        views.coach_delete,
        name="coach_delete"
    ),

    path(
        "management/coaches/add/",
        views.coach_create,
        name="coach_create"
    ),

]