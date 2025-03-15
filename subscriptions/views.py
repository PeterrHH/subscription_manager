from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from rest_framework import viewsets, filters, status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.utils import timezone
from .models import Subscription
from .serializers import SubscriptionSerializer

@login_required
def subscription_form(request):
    """Render the subscription form page"""
    return render(request, 'subscriptions/add_subscription.html')

@api_view(['GET'])
@permission_classes([AllowAny])
def home(request):
    """API home endpoint"""
    return Response({"message": "Welcome to Subscription Manager API"})

def signup(request):
    """User signup view"""
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form = UserCreationForm()
    return render(request, 'registration/signup.html', {'form': form})

class SubscriptionViewSet(viewsets.ModelViewSet):
    serializer_class = SubscriptionSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.OrderingFilter, filters.SearchFilter]
    ordering_fields = ['price', 'next_charge_date', 'service_name']
    search_fields = ['service_name', 'category']

    def get_queryset(self):
        queryset = Subscription.objects.filter(user=self.request.user)
        status = self.request.query_params.get('status', None)
        category = self.request.query_params.get('category', None)

        if status:
            queryset = queryset.filter(status=status.upper())
        if category:
            queryset = queryset.filter(category=category.upper())

        return queryset

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        subscription = self.get_object()
        subscription.status = 'CANCELED'
        subscription.cancellation_date = timezone.now().date()
        subscription.save()
        return Response(
            {'message': f'{subscription.service_name} has been canceled'},
            status=status.HTTP_200_OK
        )

    @action(detail=False, methods=['get'])
    def active(self, request):
        active_subs = self.get_queryset().filter(status='ACTIVE')
        serializer = self.get_serializer(active_subs, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def canceled(self, request):
        canceled_subs = self.get_queryset().filter(status='CANCELED')
        serializer = self.get_serializer(canceled_subs, many=True)
        return Response(serializer.data)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_subscription_api(request):
    """API endpoint to add a subscription"""
    serializer = SubscriptionSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save(user=request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)