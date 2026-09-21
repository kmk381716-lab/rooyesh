from django.db import models


class HomeBlock(models.Model):

    CONTENT_TYPES = [
        ("text", "متن"),
        ("image", "تصویر"),
        ("video", "ویدیو"),
    ]

    title = models.CharField(
        max_length=200
    )

    description = models.TextField(
        blank=True
    )

    content_type = models.CharField(
        max_length=20,
        choices=CONTENT_TYPES,
        default="text"
    )

    image = models.FileField(
        upload_to="home/images/",
        blank=True
    )

    video = models.FileField(
        upload_to="home/videos/",
        blank=True
    )

    button_text = models.CharField(
        max_length=100,
        blank=True
    )

    button_url = models.URLField(
        blank=True
    )

    is_active = models.BooleanField(
        default=True
    )

    order = models.PositiveIntegerField(
        default=0
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return self.title

class Trip(models.Model):

    title = models.CharField(
        max_length=200
    )

    description = models.TextField(
        blank=True
    )

    image = models.FileField(
        upload_to="trips/",
        blank=True
    )

    registration_url = models.URLField(
        blank=True
    )

    is_active = models.BooleanField(
        default=True
    )

    order = models.PositiveIntegerField(
        default=0
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return self.title

class SiteSettings(models.Model):

    name = models.CharField(
        max_length=100,
        default="کانون رویش"
    )

    subtitle = models.CharField(
        max_length=200,
        default="رشد، رفاقت، تجربه"
    )

    profile_image = models.ImageField(
        upload_to="site/",
        blank=True
    )

    def __str__(self):
        return self.name

