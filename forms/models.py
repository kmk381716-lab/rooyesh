import uuid

from django.conf import settings
from django.core.validators import FileExtensionValidator
from django.db import models


# =========================================================
# Form
# =========================================================
class Form(models.Model):
    uuid = models.UUIDField(
        default=uuid.uuid4,
        editable=False,
        unique=True,
        verbose_name="شناسه یکتا",
    )

    title = models.CharField(
        max_length=200,
        verbose_name="عنوان",
    )

    description = models.TextField(
        blank=True,
        verbose_name="توضیحات",
    )

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="created_forms",
        verbose_name="سازنده",
    )

    is_active = models.BooleanField(
        default=True,
        verbose_name="فعال",
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="تاریخ ایجاد",
    )

    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="آخرین ویرایش",
    )

    class Meta:
        verbose_name = "فرم"
        verbose_name_plural = "فرم‌ها"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["is_active", "-created_at"]),
        ]

    def __str__(self):
        return self.title


# =========================================================
# Question
# =========================================================
class Question(models.Model):

    class FieldType(models.TextChoices):
        TEXT = "text", "متن کوتاه"
        TEXTAREA = "textarea", "متن بلند"
        NUMBER = "number", "عدد"
        BOOLEAN = "boolean", "بله / خیر"
        SINGLE = "single", "تک انتخابی"
        MULTIPLE = "multiple", "چند انتخابی"
        DATE = "date", "تاریخ"
        FILE = "file", "فایل"

    form = models.ForeignKey(
        Form,
        on_delete=models.CASCADE,
        related_name="questions",
        verbose_name="فرم",
    )

    title = models.CharField(
        max_length=300,
        verbose_name="عنوان سؤال",
    )

    field_type = models.CharField(
        max_length=20,
        choices=FieldType.choices,
        default=FieldType.TEXT,
        verbose_name="نوع فیلد",
    )

    required = models.BooleanField(
        default=False,
        verbose_name="اجباری",
    )

    order = models.PositiveIntegerField(
        default=0,
        verbose_name="ترتیب",
    )

    class Meta:
        verbose_name = "سؤال"
        verbose_name_plural = "سؤالات"
        ordering = ["order", "id"]
        constraints = [
            models.UniqueConstraint(
                fields=["form", "order"],
                name="unique_question_order_per_form",
            ),
        ]

    def __str__(self):
        return self.title

    @property
    def is_choice(self):
        return self.field_type in (
            self.FieldType.SINGLE,
            self.FieldType.MULTIPLE,
        )


# =========================================================
# Option
# =========================================================
class Option(models.Model):
    question = models.ForeignKey(
        Question,
        on_delete=models.CASCADE,
        related_name="options",
        verbose_name="سؤال",
    )

    title = models.CharField(
        max_length=200,
        verbose_name="عنوان گزینه",
    )

    order = models.PositiveIntegerField(
        default=0,
        verbose_name="ترتیب",
    )

    class Meta:
        verbose_name = "گزینه"
        verbose_name_plural = "گزینه‌ها"
        ordering = ["order", "id"]
        constraints = [
            models.UniqueConstraint(
                fields=["question", "order"],
                name="unique_option_order_per_question",
            ),
        ]

    def __str__(self):
        return self.title


# =========================================================
# Submission
# =========================================================
class Submission(models.Model):
    form = models.ForeignKey(
        Form,
        on_delete=models.CASCADE,
        related_name="submissions",
        verbose_name="فرم",
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="form_submissions",
        verbose_name="کاربر",
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="تاریخ ثبت",
    )

    class Meta:
        verbose_name = "پاسخ فرم"
        verbose_name_plural = "پاسخ‌های فرم"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["form", "-created_at"]),
        ]

    def __str__(self):
        return f"{self.form.title} - {self.id}"


# =========================================================
# Answer
# =========================================================
class Answer(models.Model):
    submission = models.ForeignKey(
        Submission,
        on_delete=models.CASCADE,
        related_name="answers",
        verbose_name="پاسخ فرم",
    )

    question = models.ForeignKey(
        Question,
        on_delete=models.CASCADE,
        related_name="answers",
        verbose_name="سؤال",
    )

    # برای متن کوتاه / متن بلند
    text_value = models.TextField(
        blank=True,
        verbose_name="مقدار متنی",
    )

    # برای عدد
    number_value = models.DecimalField(
        max_digits=15,
        decimal_places=3,
        null=True,
        blank=True,
        verbose_name="مقدار عددی",
    )

    # برای تاریخ
    date_value = models.DateField(
        null=True,
        blank=True,
        verbose_name="مقدار تاریخ",
    )

    # برای بله / خیر
    boolean_value = models.BooleanField(
        null=True,
        blank=True,
        verbose_name="مقدار بله/خیر",
    )

    # برای فایل
    file_value = models.FileField(
        upload_to="forms/files/",
        blank=True,
        null=True,
        validators=[
            FileExtensionValidator(
                allowed_extensions=[
                    "pdf",
                    "jpg",
                    "jpeg",
                    "png",
                    "doc",
                    "docx",
                    "xls",
                    "xlsx",
                    "zip",
                ]
            )
        ],
        verbose_name="فایل",
    )

    # برای تک انتخابی / چند انتخابی
    selected_options = models.ManyToManyField(
        Option,
        blank=True,
        related_name="answers",
        verbose_name="گزینه‌های انتخاب‌شده",
    )

    class Meta:
        verbose_name = "پاسخ"
        verbose_name_plural = "پاسخ‌ها"
        constraints = [
            models.UniqueConstraint(
                fields=["submission", "question"],
                name="unique_answer_per_question",
            ),
        ]

    def __str__(self):
        return f"{self.question.title} - {self.submission.id}"

    def display_value(self):
        """نمایش تمیز پاسخ بر اساس نوع سؤال."""
        q_type = self.question.field_type

        if q_type in (Question.FieldType.TEXT, Question.FieldType.TEXTAREA):
            return self.text_value or "—"

        if q_type == Question.FieldType.NUMBER:
            return self.number_value if self.number_value is not None else "—"

        if q_type == Question.FieldType.DATE:
            return self.date_value if self.date_value else "—"

        if q_type == Question.FieldType.BOOLEAN:
            if self.boolean_value is None:
                return "—"
            return "بله" if self.boolean_value else "خیر"

        if q_type == Question.FieldType.FILE:
            return self.file_value.name if self.file_value else "—"

        if q_type == Question.FieldType.SINGLE:
            option = self.selected_options.first()
            return option.title if option else "—"

        if q_type == Question.FieldType.MULTIPLE:
            titles = list(self.selected_options.values_list("title", flat=True))
            return "، ".join(titles) if titles else "—"

        return "—"