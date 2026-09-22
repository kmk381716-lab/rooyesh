from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path


urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("home.urls")),
    path("library/", include("library.urls")),
    path("forms/", include("forms.urls")),
    path('coaches/', include('coaches.urls')),
    path("admin/",admin.site.urls),
    path("coaches/",include("coaches.urls")),
    path("students/",include("students.urls")),

]

urlpatterns += static(
    settings.MEDIA_URL,
    document_root=settings.MEDIA_ROOT
)
