from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render

from .models import Book, BorrowRequest


def library(request):
    query = request.GET.get("q", "").strip()

    books = Book.objects.filter(
        is_active=True
    )

    if query:
        books = books.filter(
            title__icontains=query
        ) | books.filter(
            author__icontains=query
        )

    books = books.order_by("title")

    return render(
        request,
        "library/library.html",
        {
            "books": books,
            "query": query,
        }
    )


def borrow_request(request, book_id):

    book = get_object_or_404(
        Book,
        id=book_id,
        is_active=True
    )

    if request.method == "POST":

        requester_name = request.POST.get(
            "requester_name",
            ""
        ).strip()

        phone = request.POST.get(
            "phone",
            ""
        ).strip()

        if not requester_name or not phone:
            messages.error(
                request,
                "لطفاً نام و شماره تماس را وارد کنید."
            )
            return redirect("library")

        if book.available_copies <= 0:
            messages.error(
                request,
                "این کتاب در حال حاضر موجود نیست."
            )
            return redirect("library")

        BorrowRequest.objects.create(
            book=book,
            requester_name=requester_name,
            phone=phone,
        )

        messages.success(
            request,
            "درخواست امانت شما ثبت شد."
        )

        return redirect("library")

    return redirect("library")