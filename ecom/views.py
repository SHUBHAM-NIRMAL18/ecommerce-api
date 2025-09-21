from rest_framework import viewsets, status, generics, permissions
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView, TokenObtainPairView
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response
from .serializers import MyTokenObtainPairSerializer


from .models import User, Category, Product, Order
from .serializers import (
    RegisterSerializer,
    CategorySerializer,
    ProductSerializer,
    OrderWriteSerializer,
    OrderReadSerializer,
    OrderChangeStatusSerializer,
)
from .permissions import IsAdminRole, IsCustomerRole


class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            self.perform_create(serializer)
            headers = self.get_success_headers(serializer.data)
            return Response(
                {
                    "message": "Registration successful!",
                    "user": serializer.data
                },
                status=status.HTTP_201_CREATED,
                headers=headers,
            )
        else:
            return Response(
                {
                    "message": "Registration failed.",
                    "errors": serializer.errors
                },
                status=status.HTTP_400_BAD_REQUEST
            )

class LoginView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
            tokens = serializer.validated_data
            return Response(
                {
                    "message": "Login successful!",
                    **tokens
                },
                status=status.HTTP_200_OK
            )
        except Exception as e:
            return Response(
                {
                    "message": "Login failed.",
                    "errors": serializer.errors
                },
                status=status.HTTP_401_UNAUTHORIZED
            )

class RefreshTokenView(TokenRefreshView):
    permission_classes = [permissions.AllowAny]
    
    
class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [IsAuthenticated()]
        return [IsAuthenticated(), IsAdminRole()]


class ProductViewSet(viewsets.ModelViewSet):
    serializer_class = ProductSerializer

    def get_queryset(self):
        qs = Product.objects.all()
        if not self.request.user.is_admin:
            return qs.filter(is_active=True)
        return qs

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [IsAuthenticated()]
        return [IsAuthenticated(), IsAdminRole()]


class OrderViewSet(viewsets.ModelViewSet):
    """
    - Customers:
      • create (validated by OrderWriteSerializer)
      • list/retrieve own orders
      • cancel own pending orders
    - Admins:
      • list/retrieve all orders
      • change_status on any order (validated by OrderChangeStatusSerializer)
    """
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return Order.objects.all() if user.is_admin else Order.objects.filter(customer=user)

    def get_serializer_class(self):
        if self.action == 'change_status':
            return OrderChangeStatusSerializer
        if self.action in ['list', 'retrieve']:
            return OrderReadSerializer
        return OrderWriteSerializer

    def get_permissions(self):
        if self.action == 'create':
            return [IsAuthenticated(), IsCustomerRole()]
        if self.action == 'cancel':
            return [IsAuthenticated(), IsCustomerRole()]
        if self.action == 'change_status':
            return [IsAuthenticated(), IsAdminRole()]
        return [IsAuthenticated()]

    def perform_create(self, serializer):
        serializer.save(customer=self.request.user)

    @action(detail=True, methods=['post'], url_path='cancel')
    def cancel(self, request, pk=None):
        order = self.get_object()
        if order.customer != request.user:
            return Response({'detail': "You can only cancel your own orders."},
                            status=status.HTTP_403_FORBIDDEN)
        if order.status != Order.STATUS_PENDING:
            return Response({'detail': "Only pending orders can be cancelled."},
                            status=status.HTTP_400_BAD_REQUEST)
        order.status = Order.STATUS_CANCELLED
        order.save(update_fields=['status'])
        return Response({'status': 'cancelled'})

    @action(detail=True, methods=['post'], url_path='change_status')
    def change_status(self, request, pk=None):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        order = self.get_object()
        order.status = serializer.validated_data['status']
        order.save(update_fields=['status'])
        return Response({'status': order.status})
