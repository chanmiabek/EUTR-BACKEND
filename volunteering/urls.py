from rest_framework.routers import DefaultRouter
from .views import OpportunityViewSet


router = DefaultRouter()
router.include_format_suffixes = False
router.register(r'volunteering', OpportunityViewSet, basename='volunteering')

urlpatterns = router.urls
