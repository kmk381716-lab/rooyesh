from django.db import models


class MembershipFeeSetting(models.Model):

    amount = models.PositiveBigIntegerField(
        verbose_name="مبلغ حق عضویت"
    )

    is_active = models.BooleanField(
        default=True,
        verbose_name="فعال"
    )

    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="آخرین بروزرسانی"
    )

    class Meta:
        verbose_name = "تنظیم حق عضویت"
        verbose_name_plural = "تنظیمات حق عضویت"

    def __str__(self):
        return f"{self.amount:,} تومان"

from django.contrib.auth.models import User
from django.db import models

from students.models import Student


class MembershipFeeSetting(models.Model):

    amount = models.PositiveBigIntegerField(
        verbose_name="مبلغ حق عضویت"
    )

    is_active = models.BooleanField(
        default=True,
        verbose_name="فعال"
    )

    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="آخرین بروزرسانی"
    )

    class Meta:
        verbose_name = "تنظیم حق عضویت"
        verbose_name_plural = "تنظیمات حق عضویت"

    def __str__(self):
        return f"{self.amount:,} تومان"


class Charge(models.Model):

    CHARGE_TYPES = [
        ("membership", "حق عضویت"),
        ("trip", "اردو"),
        ("other", "سایر"),
    ]

    student = models.ForeignKey(
        Student,
        on_delete=models.PROTECT,
        related_name="charges",
        verbose_name="دانش‌آموز"
    )

    charge_type = models.CharField(
        max_length=20,
        choices=CHARGE_TYPES,
        verbose_name="نوع بدهی"
    )

    title = models.CharField(
        max_length=200,
        verbose_name="عنوان"
    )

    amount = models.PositiveBigIntegerField(
        verbose_name="مبلغ"
    )

    description = models.TextField(
        blank=True,
        verbose_name="توضیحات"
    )

    created_by = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name="created_charges",
        verbose_name="ثبت‌کننده"
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="تاریخ ثبت"
    )

    class Meta:
        verbose_name = "بدهی"
        verbose_name_plural = "بدهی‌ها"

        ordering = [
            "-created_at"
        ]

    def __str__(self):
        return (
            f"{self.student} - "
            f"{self.title} - "
            f"{self.amount:,} تومان"
        )

    @property
    def paid_amount(self):
        return sum(
            payment.amount
            for payment in self.payments.all()
        )

    @property
    def remaining_amount(self):
        remaining = self.amount - self.paid_amount

        return max(
            remaining,
            0
        )


class Payment(models.Model):

    charge = models.ForeignKey(
        Charge,
        on_delete=models.PROTECT,
        related_name="payments",
        verbose_name="بدهی مربوطه"
    )

    amount = models.PositiveBigIntegerField(
        verbose_name="مبلغ پرداخت"
    )

    description = models.TextField(
        blank=True,
        verbose_name="توضیحات"
    )

    created_by = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name="created_payments",
        verbose_name="ثبت‌کننده"
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="تاریخ پرداخت"
    )

    class Meta:
        verbose_name = "پرداخت"
        verbose_name_plural = "پرداخت‌ها"

        ordering = [
            "-created_at"
        ]

    def __str__(self):
        return (
            f"{self.charge.student} - "
            f"{self.amount:,} تومان"
        )