from rest_framework.routers import DefaultRouter
from .views import PostViewSet

router = DefaultRouter()
router.include_format_suffixes = False
router.register(r'posts', PostViewSet, basename='posts')

urlpatterns = router.urls
