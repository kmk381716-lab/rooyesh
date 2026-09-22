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
        "add/",
        views.student_create,
        name="create"
    ),

    path(
        "<int:student_id>/delete/",
        views.student_delete,
        name="delete"
    ),
    path(
        "<int:student_id>/",
        views.student_detail,
        name="detail"
    ),
    path(
        "attendance/",
        views.attendance_create,
        name="attendance_create"
    ),

]