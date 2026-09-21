from django.urls import path
from . import views


urlpatterns = [
    path("", views.library, name="library"),

    path(
        "request/<int:book_id>/",
        views.borrow_request,
        name="borrow_request"
    ),
]