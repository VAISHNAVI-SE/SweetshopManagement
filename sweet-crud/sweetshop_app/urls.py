from django.urls import path
from .views import RegisterView, SweetListCreateView, SweetDetailView, PurchaseView, RestockView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework.routers import DefaultRouter
from .views import SweetViewSet

router = DefaultRouter()
router.register(r'sweets', SweetViewSet)

urlpatterns = [
    path('auth/register/', RegisterView.as_view(), name='register'),
    path('auth/login/', TokenObtainPairView.as_view(), name='login'),        
    path('auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    path('sweets/', SweetListCreateView.as_view(), name='sweet-list'),
    path('sweets/<int:pk>/', SweetDetailView.as_view(), name='sweet-detail'),

    path('sweets/<int:pk>/purchase/', PurchaseView.as_view(), name='sweet-purchase'),
    path('sweets/<int:pk>/restock/', RestockView.as_view(), name='sweet-restock'),
]
