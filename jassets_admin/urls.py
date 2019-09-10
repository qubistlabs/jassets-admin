from django.contrib import admin
from django.urls import path

from validation.views import check_validation_results

urlpatterns = [
    path('admin/', admin.site.urls),
    path('check_validation_results/', check_validation_results),
]
