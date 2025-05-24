from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    CategoryList, CategoryDetail, CategoryViewSet,
    TransactionViewSet, BudgetViewSet, DashboardView,
    UserView, CustomTokenObtainPairView, LogoutView,
    RootAPIView
)

router = DefaultRouter()
router.register(r'transactions', TransactionViewSet, basename='transaction')
router.register(r'categories', CategoryViewSet, basename='category')
router.register(r'budgets', BudgetViewSet, basename='budget')

urlpatterns = [
    path('', RootAPIView.as_view(), name='api-root'),
    path('', include(router.urls)),
    path('auth/login/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('auth/logout/', LogoutView.as_view(), name='auth_logout'),
    path('auth/user/', UserView.as_view(), name='user'),
    path('dashboard/', DashboardView.as_view(), name='dashboard'),
] 