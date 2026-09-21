from django.db import models

# Create your models here.
from django.db import models


class Book(models.Model):

    title = models.CharField(
        max_length=200
    )

    author = models.CharField(
        max_length=150,
        blank=True
    )

    description = models.TextField(
        blank=True
    )

    cover = models.ImageField(
        upload_to="library/covers/",
        blank=True
    )

    total_copies = models.PositiveIntegerField(
        default=1
    )

    available_copies = models.PositiveIntegerField(
        default=1
    )

    is_active = models.BooleanField(
        default=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    @property
    def borrowed_copies(self):
        return self.total_copies - self.available_copies

    def __str__(self):
        return self.title
class BorrowRequest(models.Model):

    STATUS_CHOICES = [
        ("pending", "در انتظار بررسی"),
        ("approved", "تأیید شده"),
        ("rejected", "رد شده"),
        ("returned", "بازگردانده شده"),
    ]

    book = models.ForeignKey(
        Book,
        on_delete=models.CASCADE,
        related_name="borrow_requests"
    )

    requester_name = models.CharField(
        max_length=150
    )

    phone = models.CharField(
        max_length=20
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="pending"
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return f"{self.requester_name} - {self.book.title}"