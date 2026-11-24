from django.conf import settings
from django.contrib import admin
from django.urls import include, path, re_path
from django.views.static import serve

from portfolio.admin import publish_view

urlpatterns = [
    path("admin/publish/", admin.site.admin_view(publish_view), name="studio_publish"),
    path("admin/", admin.site.urls),
    path("", include("portfolio.urls")),
    # Uploaded images/files. Fine for a small personal site; put a CDN or
    # object storage in front of /media/ if traffic grows.
    re_path(r"^media/(?P<path>.*)$", serve, {"document_root": settings.MEDIA_ROOT}),
]

handler404 = "portfolio.views.not_found"
