from django.shortcuts import render
from .models import HomeBlock, Trip , SiteSettings


def home(request):
    blocks = HomeBlock.objects.filter(
        is_active=True
    ).order_by("order")

    trips = Trip.objects.filter(
        is_active=True
    ).order_by("order")

    site_settings = SiteSettings.objects.first()

    return render(
        request,
        "home/home.html",
        {
            "blocks": blocks,
            "trips": trips,
            "site_settings": site_settings,
        }
    )