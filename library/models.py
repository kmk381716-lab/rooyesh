from django.db import models


class Book(models.Model):

    title = models.CharField(
        max_length=200,
        verbose_name="عنوان کتاب"
    )

    author = models.CharField(
        max_length=150,
        verbose_name="نویسنده"
    )

    category = models.CharField(
        max_length=100,
        verbose_name="دسته‌بندی"
    )

    total_copies = models.PositiveIntegerField(
        default=1,
        verbose_name="تعداد نسخه"
    )

    available_copies = models.PositiveIntegerField(
        default=1,
        verbose_name="نسخه موجود"
    )

    description = models.TextField(
        blank=True,
        verbose_name="توضیحات"
    )

    is_active = models.BooleanField(
        default=True,
        verbose_name="فعال"
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="تاریخ ثبت"
    )

    def __str__(self):
        return self.title