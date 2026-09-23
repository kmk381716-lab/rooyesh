from django.urls import path

from . import views


app_name = "finance"


urlpatterns = [

    path(
        "membership-fee/",
        views.membership_fee,
        name="membership_fee"
    ),
    path(
        "charges/create/",
        views.charge_create,
        name="charge_create"
    ),
    path(
        "student/<int:student_id>/",
        views.student_finance,
        name="student_finance"
    ),
    path(
        "charge/<int:charge_id>/payment/",
        views.payment_create,
        name="payment_create"
    ),

    path(
    "membership-fee/apply/",
    views.apply_membership_fee,
    name="apply_membership_fee"
    ),

]
