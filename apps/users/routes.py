from rest_framework.routers import DefaultRouter

from apps.users.views import AuthViewSet, UserViewSet, AdminViewSet

router = DefaultRouter()

router.register(r"auth", AuthViewSet, basename="auth-api")
router.register(r"users", UserViewSet, basename="user-api")
router.register(r"admin", AdminViewSet, basename="admin-api")
