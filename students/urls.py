from django.urls import path

from . import views


app_name = "students"


urlpatterns = [

    path(
        "",
        views.student_list,
        name="list"
    ),

    path(
        "create/",
        views.student_create,
        name="create"
    ),

    path(
        "<int:student_id>/",
        views.student_detail,
        name="detail"
    ),

    path(
        "attendance/create/",
        views.attendance_create,
        name="attendance_create"
    ),

    path(
        "<int:student_id>/delete/",
        views.student_delete,
        name="delete"
    ),

    path(
        "groups/",
        views.group_management,
        name="group_management"
    ),

    path(
        "groups/create/",
        views.group_create,
        name="group_create"
    ),

    path(
        "groups/<int:group_id>/edit/",
        views.group_edit,
        name="group_edit"
    ),

    path(
        "groups/<int:group_id>/toggle/",
        views.group_toggle,
        name="group_toggle"
    ),
    path(
        "all/",
        views.all_students,
        name="all_students"
    ),
]