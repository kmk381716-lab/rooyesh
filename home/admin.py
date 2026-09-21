from django.contrib import admin
from .models import HomeBlock, Trip, SiteSettings


admin.site.register(HomeBlock)
admin.site.register(Trip)
admin.site.register(SiteSettings)