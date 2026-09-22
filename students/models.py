from django.contrib.auth.models import User
from django.db import models


class Student(models.Model):

    coach = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="students",
        verbose_name="مربی"
    )

    first_name = models.CharField(
        max_length=100,
        verbose_name="نام"
    )

    last_name = models.CharField(
        max_length=100,
        verbose_name="نام خانوادگی"
    )

    grade = models.CharField(
        max_length=50,
        verbose_name="پایه"
    )

    phone = models.CharField(
        max_length=20,
        blank=True,
        verbose_name="شماره تماس دانش‌آموز"
    )

    parent_phone = models.CharField(
        max_length=20,
        blank=True,
        verbose_name="شماره تماس والدین"
    )

    is_active = models.BooleanField(
        default=True,
        verbose_name="فعال"
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="تاریخ ثبت"
    )

    class Meta:
        verbose_name = "دانش‌آموز"
        verbose_name_plural = "دانش‌آموزان"

        ordering = [
            "first_name",
            "last_name"
        ]

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

class Attendance(models.Model):

    ATTENDANCE_TYPES = [
        ("heyat", "هیئت"),
        ("weekly_class", "کلاس هفتگی"),
        ("meeting", "قرار"),
    ]

    STATUS_CHOICES = [
        ("present", "حاضر"),
        ("absent", "غایب"),
        ("excused", "موجه"),
    ]

    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        related_name="attendances",
        verbose_name="دانش‌آموز"
    )

    attendance_type = models.CharField(
        max_length=30,
        choices=ATTENDANCE_TYPES,
        verbose_name="نوع برنامه"
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        verbose_name="وضعیت حضور"
    )

    date = models.DateField(
        verbose_name="تاریخ"
    )

    title = models.CharField(
        max_length=200,
        blank=True,
        verbose_name="عنوان برنامه"
    )

    note = models.TextField(
        blank=True,
        verbose_name="توضیحات"
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="تاریخ ثبت"

    )

    class Meta:
        verbose_name = "حضور و غیاب"
        verbose_name_plural = "حضور و غیاب"

        ordering = [
            "-date"
        ]

        constraints = [
            models.UniqueConstraint(
                fields=[
                    "student",
                    "attendance_type",
                    "date"
                ],
                name="unique_student_attendance_per_type_date"
            )
        ]

    def __str__(self):
        return (
            f"{self.student} - "
            f"{self.get_attendance_type_display()} - "
            f"{self.date}"
        )