from django.urls import path

from . import views


app_name = "forms"


urlpatterns = [

    # لیست فرم‌ها
    path(
        "",
        views.form_list,
        name="form_list",
    ),

    # ساخت فرم
    path(
        "builder/",
        views.builder,
        name="builder",
    ),

    # پاسخ‌ها
    path(
        "responses/",
        views.response_dashboard,
        name="responses",
    ),

    # جزئیات پاسخ
    path(
        "responses/submission/<int:submission_id>/",
        views.submission_detail,
        name="submission_detail",
    ),

    # حذف پاسخ
    path(
        "responses/submission/<int:submission_id>/delete/",
        views.delete_submission,
        name="delete_submission",
    ),

    # حذف فرم
    path(
        "<int:form_id>/delete/",
        views.delete_form,
        name="delete_form",
    ),

    # پر کردن فرم
    path(
        "<int:form_id>/",
        views.fill_form,
        name="fill_form",
    ),
]