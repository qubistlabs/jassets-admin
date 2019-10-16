from django.contrib import admin
from django.urls import path, re_path
from django.views.generic import RedirectView
from django.views.static import serve
from django.conf import settings

urlpatterns = [
    path('', RedirectView.as_view(url='admin/')),
    path('admin/', admin.site.urls),
]

if not settings.DEBUG:
    urlpatterns += [
        re_path(r'^static/(?P<path>.*)$', serve, {
            'document_root': settings.STATIC_ROOT,
        }),
    ]
