"""
URL configuration for educate_us_rise_us project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
# from rest_framework.urlpatterns import format_suffix_patterns
from django.http import JsonResponse

# A tiny view just to test the home page
def api_root(request):
    return JsonResponse({"message": "Welcome to the CBO API", "status": "running"})

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/auth/', include('accounts.urls')),
    path('api/', include('posts.urls')),
    path('api/', include('volunteering.urls')),
    path('api/', include('donations.urls')),
    path('api/auth/',include('members.urls')), # This is usually for DRF login
    path('api/auth/', include('rest_framework.urls')), # This is usually for DRF login

]


# urlpatterns = format_suffix_patterns(urlpatterns)


if settings.DEBUG:
   urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
