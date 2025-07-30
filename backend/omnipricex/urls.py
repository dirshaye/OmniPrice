from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from django.http import HttpResponse

from api.views import (
    ProductViewSet, CompetitorViewSet, PricingRuleViewSet, 
    PricingDecisionViewSet, bulk_price_optimization, index
)

# Create DRF router
router = DefaultRouter()
router.register(r'products', ProductViewSet)
router.register(r'competitors', CompetitorViewSet)
router.register(r'pricing-rules', PricingRuleViewSet)
router.register(r'pricing-decisions', PricingDecisionViewSet)

def metrics_view(request):
    """Endpoint for Prometheus metrics"""
    from metrics.collectors import MetricsCollector
    metrics = MetricsCollector.get_metrics()
    return HttpResponse(metrics, content_type='text/plain')

urlpatterns = [
    # Admin
    path('admin/', admin.site.urls),
    
    # Authentication
    path('api/auth/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    # API endpoints
    path('api/', include(router.urls)),
    path('api/bulk-price-optimization/', bulk_price_optimization, name='bulk_price_optimization'),
    
    # Metrics
    path('metrics/', metrics_view, name='metrics'),
    
    # Frontend
    path('', index, name='index'),
]