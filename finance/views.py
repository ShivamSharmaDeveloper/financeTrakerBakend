from django.shortcuts import render
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated, AllowAny
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
from django.contrib.auth.models import User
from .utils import get_default_categories
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.views import APIView

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

    def get_default_categories(self):
        return get_default_categories()

    @action(detail=False, methods=['post'])
    def initialize_defaults(self, request):
        categories_created = 0
        default_categories = self.get_default_categories()

        for category_data in default_categories:
            _, created = Category.objects.get_or_create(
                name=category_data['name'],
                user=request.user,
                defaults={
                    'description': category_data['description'],
                    'type': category_data['type']
                }
            )
            if created:
                categories_created += 1

        return Response({
            'message': f'{categories_created} default categories have been created.',
            'total_categories': Category.objects.filter(user=request.user).count()
        })

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        if not queryset.exists():
            return Response({
                'results': [],
                'message': 'No categories found. Would you like to initialize default categories?',
                'can_initialize_defaults': True
            }, status=status.HTTP_200_OK)
        serializer = self.get_serializer(queryset, many=True)
        return Response({
            'results': serializer.data
        })

class TransactionFilter(filters.FilterSet):
    search = filters.CharFilter(method='filter_search')
    min_date = filters.DateFilter(field_name='date', lookup_expr='gte')
    max_date = filters.DateFilter(field_name='date', lookup_expr='lte')
    start_date = filters.DateFilter(field_name='date', lookup_expr='gte')
    end_date = filters.DateFilter(field_name='date', lookup_expr='lte')
    min_amount = filters.NumberFilter(field_name='amount', lookup_expr='gte')
    max_amount = filters.NumberFilter(field_name='amount', lookup_expr='lte')
    
    def filter_search(self, queryset, name, value):
        if value:
            return queryset.filter(
                Q(description__icontains=value) |
                Q(category__name__icontains=value)
            )
        return queryset

    class Meta:
        model = Transaction
        fields = [
            'category', 'type', 
            'min_date', 'max_date', 
            'start_date', 'end_date',
            'min_amount', 'max_amount',
            'search'
        ]

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

    @action(detail=False, methods=['get'])
    def monthly_trends(self, request):
        # Get the last 6 months of data
        end_date = timezone.now().date()
        start_date = end_date.replace(day=1)
        start_date = start_date.replace(month=start_date.month - 5) if start_date.month > 6 else \
                    start_date.replace(year=start_date.year - 1, month=start_date.month + 7)

        # Get all transactions in the date range
        transactions = self.get_queryset().filter(
            date__range=[start_date, end_date]
        )

        # Initialize monthly data
        monthly_data = []
        current_date = start_date
        
        while current_date <= end_date:
            month_start = current_date.replace(day=1)
            if current_date.month == 12:
                month_end = current_date.replace(year=current_date.year + 1, month=1, day=1)
            else:
                month_end = current_date.replace(month=current_date.month + 1, day=1)
            month_end = month_end - timezone.timedelta(days=1)

            # Get month's transactions
            month_transactions = transactions.filter(
                date__range=[month_start, month_end]
            )

            # Calculate income and expenses
            income = month_transactions.filter(type='income').aggregate(
                total=Sum('amount'))['total'] or 0
            expenses = month_transactions.filter(type='expense').aggregate(
                total=Sum('amount'))['total'] or 0

            # Format month name
            month_name = current_date.strftime('%b %Y')

            monthly_data.append({
                'month': month_name,
                'income': float(income),
                'expenses': float(expenses),
                'savings': float(income - expenses)
            })

            # Move to next month
            if current_date.month == 12:
                current_date = current_date.replace(year=current_date.year + 1, month=1)
            else:
                current_date = current_date.replace(month=current_date.month + 1)

        return Response(monthly_data)

class BudgetViewSet(viewsets.ModelViewSet):
    serializer_class = BudgetSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Budget.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def create(self, request, *args, **kwargs):
        # Check if budget already exists for this category and month
        category_id = request.data.get('category')
        start_date = request.data.get('start_date')
        end_date = request.data.get('end_date')
        
        existing_budget = Budget.objects.filter(
            user=request.user,
            category_id=category_id,
            start_date__lte=end_date,
            end_date__gte=start_date
        ).first()

        if existing_budget:
            # Update existing budget
            serializer = self.get_serializer(existing_budget, data=request.data)
            serializer.is_valid(raise_exception=True)
            self.perform_update(serializer)
        else:
            # Create new budget
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)

        return Response(serializer.data)

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

    @action(detail=False, methods=['get'])
    def summary(self, request):
        # Get current month's budgets
        today = timezone.now().date()
        start_date = today.replace(day=1)
        end_date = (start_date.replace(month=start_date.month + 1) - timezone.timedelta(days=1))

        # Get all expense transactions for the current month
        transactions = Transaction.objects.filter(
            user=request.user,
            type='expense',
            date__range=[start_date, end_date]
        )

        # Get expenses by category
        expenses_by_category = transactions.values(
            'category',
            'category__name'
        ).annotate(
            total_spent=Sum('amount')
        )

        # Get existing budgets
        budgets = self.get_queryset().filter(
            start_date__lte=end_date,
            end_date__gte=start_date
        ).select_related('category')

        # Create a map of category_id to budget amount
        budget_map = {budget.category_id: float(budget.amount) for budget in budgets}

        # Initialize summary data
        summary_data = {
            'budgeted': 0,
            'spent': 0,
            'remaining': 0,
            'categories': []
        }

        # Process each category that has expenses
        for expense in expenses_by_category:
            category_id = expense['category']
            category_name = expense['category__name']
            spent = float(expense['total_spent'])
            
            # Get budget amount if it exists, otherwise use spent amount as budget
            budget_amount = budget_map.get(category_id, spent)
            remaining = budget_amount - spent

            # Add to totals
            summary_data['budgeted'] += budget_amount
            summary_data['spent'] += spent
            
            # Add category details
            summary_data['categories'].append({
                'name': category_name,
                'budget': budget_amount,
                'spent': spent,
                'remaining': remaining
            })

        # Add categories that have budgets but no expenses
        for budget in budgets:
            if budget.category_id not in [exp['category'] for exp in expenses_by_category]:
                summary_data['budgeted'] += float(budget.amount)
                summary_data['categories'].append({
                    'name': budget.category.name,
                    'budget': float(budget.amount),
                    'spent': 0,
                    'remaining': float(budget.amount)
                })

        # Calculate total remaining
        summary_data['remaining'] = summary_data['budgeted'] - summary_data['spent']

        return Response(summary_data)

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
        try:
            # First, validate credentials and get tokens
            response = super().post(request, *args, **kwargs)
            
            if response.status_code == 200:
                # Only if authentication was successful, add user data
                User = get_user_model()
                try:
                    user = User.objects.get(username=request.data.get('username'))
                    user_serializer = UserSerializer(user)
                    response.data['user'] = user_serializer.data
                except User.DoesNotExist:
                    response.data['user'] = None
                    
            return response
            
        except Exception as e:
            # Return the original error response
            return Response(
                {"detail": "Invalid credentials"},
                status=401
            )

class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            # Get the refresh token from the request
            refresh_token = request.data.get('refresh_token')
            
            if refresh_token:
                # Blacklist the refresh token
                token = RefreshToken(refresh_token)
                token.blacklist()
            
            return Response({
                'message': 'Successfully logged out'
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({
                'message': 'Error logging out',
                'error': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)

class RootAPIView(APIView):
    permission_classes = [AllowAny]
    
    def get(self, request):
        return Response({
            'status': 'ok',
            'version': '1.0',
            'endpoints': {
                'auth': {
                    'login': '/api/auth/login/',
                    'logout': '/api/auth/logout/',
                    'user': '/api/auth/user/'
                },
                'categories': '/api/categories/',
                'transactions': '/api/transactions/',
                'budgets': '/api/budgets/',
                'dashboard': '/api/dashboard/'
            }
        })
