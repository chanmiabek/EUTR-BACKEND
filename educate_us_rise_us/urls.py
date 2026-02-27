from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.http import JsonResponse
from django.urls import include, path

from donations.views import MpesaWebhookView


def api_root(request):
    return JsonResponse({"message": "Welcome to the EUTR", "status": "running"})


urlpatterns = [
    path("", api_root, name="api-root"),
    path("admin/", admin.site.urls),
    path("summernote/", include("django_summernote.urls")),
    path("mpesa-express-simulate/", MpesaWebhookView.as_view(), name="mpesa-express-simulate"),
    path("api/auth/", include("accounts.urls")),
    path("api/auth/", include("rest_framework.urls")),
    path("api/", include("members.urls")),
    path("api/", include("posts.urls")),
    path("api/", include("volunteering.urls")),
    path("api/", include("donations.urls")),
    path("api/", include("applications.urls")),
    path("api/", include("eventmedia.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
