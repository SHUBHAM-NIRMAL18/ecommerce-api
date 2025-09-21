from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import RegisterView, LoginView, RefreshTokenView,CategoryViewSet, ProductViewSet, OrderViewSet

router = DefaultRouter()
router.register('categories', CategoryViewSet, basename='category')
router.register('products', ProductViewSet, basename = 'product')
router.register('orders', OrderViewSet, basename='order')

urlpatterns = [
    path('register/', RegisterView.as_view(),name='register'),
    path('login/',LoginView.as_view(),name='token_obtain_pair'),
    path('token/refresh/',RefreshTokenView.as_view(),name='token_refresh'),
    
    path('', include(router.urls)),
]
