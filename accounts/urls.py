from django.urls import path
from .views import RegisterView, LoginView, MeView
from rest_framework_simplejwt.views import TokenRefreshView
from rest_framework.urlpatterns import format_suffix_patterns

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('me/', MeView.as_view(), name='me'),
]


urlpatterns = format_suffix_patterns(urlpatterns)