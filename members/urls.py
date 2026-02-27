from rest_framework.routers import DefaultRouter
from .views import MemberProfileViewSet

router = DefaultRouter()
router.include_format_suffixes = False
router.register(r'members', MemberProfileViewSet, basename='members')

urlpatterns = router.urls
