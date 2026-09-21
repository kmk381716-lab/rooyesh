from django.db import models
from django.contrib.auth.models import User


class Form(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)

    created_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='created_forms'
    )

    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title


class Question(models.Model):

    FIELD_TYPES = [
        ('text', 'متن کوتاه'),
        ('textarea', 'متن بلند'),
        ('number', 'عدد'),
        ('boolean', 'بله / خیر'),
        ('single', 'تک انتخابی'),
        ('multiple', 'چند انتخابی'),
        ('date', 'تاریخ'),
        ('file', 'فایل'),
    ]

    form = models.ForeignKey(
        Form,
        on_delete=models.CASCADE,
        related_name='questions'
    )

    title = models.CharField(max_length=300)

    field_type = models.CharField(
        max_length=20,
        choices=FIELD_TYPES
    )

    required = models.BooleanField(default=False)

    order = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.title


class Option(models.Model):
    question = models.ForeignKey(
        Question,
        on_delete=models.CASCADE,
        related_name='options'
    )

    title = models.CharField(max_length=200)

    order = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.title


class Submission(models.Model):
    form = models.ForeignKey(
        Form,
        on_delete=models.CASCADE,
        related_name='submissions'
    )

    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='form_submissions'
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.form.title} - {self.id}'


class Answer(models.Model):
    submission = models.ForeignKey(
        Submission,
        on_delete=models.CASCADE,
        related_name='answers'
    )

    question = models.ForeignKey(
        Question,
        on_delete=models.CASCADE,
        related_name='answers'
    )

    text_value = models.TextField(blank=True)

    file_value = models.FileField(
        upload_to='forms/files/',
        blank=True,
        null=True
    )

    def __str__(self):
        return f'{self.question.title} - {self.submission.id}'