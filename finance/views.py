from django.shortcuts import render
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from .models import Category
from .serializers import CategorySerializer
from django.db.models import Sum, F, Q
from django.utils import timezone
from rest_framework import viewsets, status, views
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters import rest_framework as filters
from .models import Transaction, Budget
from .serializers import (
    TransactionSerializer, BudgetSerializer,
    DashboardSerializer, UserSerializer
)
from rest_framework_simplejwt.views import TokenObtainPairView
from django.contrib.auth import get_user_model

# Create your views here.

class CategoryList(generics.ListCreateAPIView):
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Category.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class CategoryDetail(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Category.objects.filter(user=self.request.user)

class CategoryViewSet(viewsets.ModelViewSet):
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Category.objects.filter(user=self.request.user)

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        if not queryset.exists():
            return Response({
                'results': [],
                'message': 'No categories found. Please create some categories first.'
            }, status=status.HTTP_200_OK)
        serializer = self.get_serializer(queryset, many=True)
        return Response({
            'results': serializer.data
        })

class TransactionFilter(filters.FilterSet):
    min_date = filters.DateFilter(field_name='date', lookup_expr='gte')
    max_date = filters.DateFilter(field_name='date', lookup_expr='lte')
    min_amount = filters.NumberFilter(field_name='amount', lookup_expr='gte')
    max_amount = filters.NumberFilter(field_name='amount', lookup_expr='lte')
    
    class Meta:
        model = Transaction
        fields = ['category', 'type', 'min_date', 'max_date', 'min_amount', 'max_amount']

class TransactionViewSet(viewsets.ModelViewSet):
    serializer_class = TransactionSerializer
    permission_classes = [IsAuthenticated]
    filterset_class = TransactionFilter

    def get_queryset(self):
        return Transaction.objects.filter(user=self.request.user)

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        
        if not queryset.exists():
            return Response({
                'results': [],
                'message': 'No transactions found.'
            }, status=status.HTTP_200_OK)
            
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

class BudgetViewSet(viewsets.ModelViewSet):
    serializer_class = BudgetSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Budget.objects.filter(user=self.request.user)

    def get_serializer_context(self):
        context = super().get_serializer_context()
        if self.action in ['list', 'retrieve']:
            # Calculate spent and remaining amounts for each budget
            for budget in self.get_queryset():
                expenses = Transaction.objects.filter(
                    user=self.request.user,
                    category=budget.category,
                    type='expense',
                    date__range=[budget.start_date, budget.end_date]
                ).aggregate(total=Sum('amount'))
                
                spent = expenses['total'] or 0
                budget.spent_amount = spent
                budget.remaining_amount = budget.amount - spent
        return context

class DashboardView(views.APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            # Get date range (default to current month)
            today = timezone.now().date()
            start_date = request.query_params.get('start_date', today.replace(day=1))
            end_date = request.query_params.get('end_date', today)

            # Calculate totals
            transactions = Transaction.objects.filter(
                user=request.user,
                date__range=[start_date, end_date]
            )
            
            income = transactions.filter(type='income').aggregate(
                total=Sum('amount'))['total'] or 0
            expenses = transactions.filter(type='expense').aggregate(
                total=Sum('amount'))['total'] or 0
            
            # Get expenses by category
            expenses_by_category = transactions.filter(
                type='expense'
            ).values(
                'category__name'
            ).annotate(
                total=Sum('amount')
            ).order_by('-total')

            # Format expenses by category
            expenses_dict = {
                item['category__name']: float(item['total'])
                for item in expenses_by_category
            }

            # Get recent transactions
            recent_transactions = transactions.order_by('-date', '-created_at')[:5]

            data = {
                'total_income': income,
                'total_expenses': expenses,
                'net_savings': income - expenses,
                'expenses_by_category': expenses_dict,
                'recent_transactions': recent_transactions
            }

            serializer = DashboardSerializer(data)
            return Response(serializer.data)
        except Exception as e:
            return Response({
                'error': str(e),
                'message': 'Error fetching dashboard data'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class UserView(views.APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            serializer = UserSerializer(request.user)
            return Response(serializer.data)
        except Exception as e:
            return Response({
                'error': str(e),
                'message': 'Error fetching user data'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def patch(self, request):
        try:
            serializer = UserSerializer(request.user, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({
                'error': str(e),
                'message': 'Error updating user data'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class CustomTokenObtainPairView(TokenObtainPairView):
    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        if response.status_code == 200:
            # Get the user based on the username from the request
            User = get_user_model()
            try:
                user = User.objects.get(username=request.data.get('username'))
                user_serializer = UserSerializer(user)
                response.data['user'] = user_serializer.data
            except User.DoesNotExist:
                response.data['user'] = None
        return response
