# bulletin/urls.py
from rest_framework.routers import DefaultRouter
from rest_framework_nested.routers import NestedDefaultRouter

from .apps import BulletinConfig
from .views import BulletinViewSet, ReviewViewSet

app_name = BulletinConfig.name

# Основной роутер
router = DefaultRouter()
router.register(r"bulletins", BulletinViewSet, basename="bulletins")  # /api/bulletin/bulletins/ - CRUD
router.register(r"reviews", ReviewViewSet, basename="reviews")  # /api/bulletin/reviews/ - CRUD

# Вложенный роутер для отзывов
bulletins_router = NestedDefaultRouter(router, r"bulletins", lookup="bulletin")  # /api/bulletin/bulletins/<id>/
bulletins_router.register(
    r"reviews", ReviewViewSet, basename="bulletin-reviews"
)  # /api/bulletin/bulletins/<id>/reviews/

urlpatterns = router.urls + bulletins_router.urls
