from django.urls import path

from . import views


app_name = "forms"


urlpatterns = [

    # =========================================================
    # لیست فرم‌ها
    # =========================================================
    path(
        "",
        views.form_list,
        name="form_list",
    ),

    # =========================================================
    # ساخت فرم
    # =========================================================
    path(
        "builder/",
        views.builder,
        name="builder",
    ),

    # صفحه موفقیت ساخت فرم
    path(
        "builder/success/<uuid:form_uuid>/",
        views.builder_success,
        name="builder_success",
    ),

    # =========================================================
    # پاسخ‌ها (داشبورد ادمین)
    # =========================================================
    path(
        "responses/",
        views.response_dashboard,
        name="responses",
    ),

    # جزئیات یک پاسخ
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

    # =========================================================
    # حذف فرم
    # =========================================================
    path(
        "<int:form_id>/delete/",
        views.delete_form,
        name="delete_form",
    ),

    # =========================================================
    # صفحه موفقیت ثبت پاسخ (بعد از پر کردن فرم)
    # =========================================================
    path(
        "success/<uuid:form_uuid>/",
        views.submission_success,
        name="submission_success",
    ),

    # =========================================================
    # پر کردن فرم (عمومی)
    # ⚠️ باید آخرین مسیر باشد تا با بقیه تداخل نکند
    # =========================================================
    path(
        "f/<uuid:form_uuid>/",
        views.fill_form,
        name="fill_form",
    ),
]