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
# ecom/views.py
from django.http import HttpResponse

def api_home(request):
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>🛍️ My E-Commerce API</title>
        <style>
            body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; margin: 40px; line-height: 1.7; background: #f9f9f9; color: #333; }
            h1 { color: #2c3e50; border-bottom: 3px solid #3498db; padding-bottom: 10px; }
            h2 { color: #2980b9; margin-top: 30px; }
            ul { padding-left: 20px; }
            li { margin: 8px 0; }
            code { background: #ecf0f1; padding: 2px 6px; border-radius: 4px; font-family: monospace; }
            a { color: #3498db; text-decoration: none; font-weight: 500; }
            a:hover { text-decoration: underline; }
            .container { max-width: 900px; margin: 0 auto; background: white; padding: 30px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.05); }
            .badge { display: inline-block; background: #e74c3c; color: white; padding: 3px 8px; border-radius: 4px; font-size: 0.8em; margin-left: 8px; }
            footer { margin-top: 40px; padding-top: 20px; border-top: 1px solid #eee; color: #7f8c8d; font-size: 0.9em; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🛍️ Welcome to My E-Commerce API</h1>
            <p>This is a secure, role-based REST API built with Django REST Framework.</p>

            <h2>🔐 Authentication</h2>
            <ul>
                <li><code>POST /api/v1/register/</code> — Register new user</li>
                <li><code>POST /api/v1/login/</code> — Login & get JWT tokens</li>
                <li><code>POST /api/v1/token/refresh/</code> — Refresh access token</li>
            </ul>

            <h2>📚 Interactive Documentation</h2>
            <ul>
                <li><a href="/api/docs/">Swagger UI</a> — Try live requests</li>
                <li><a href="/api/schema/">Download OpenAPI Schema (JSON)</a></li>
            </ul>

            <h2>📦 Categories</h2>
            <ul>
                <li><code>GET /api/v1/categories/</code> — List all (authenticated)</li>
                <li><code>POST /api/v1/categories/</code> — Create (admin only) <span class="badge">ADMIN</span></li>
                <li><code>GET /api/v1/categories/&lt;id&gt;/</code> — Retrieve</li>
                <li><code>PUT,PATCH /api/v1/categories/&lt;id&gt;/</code> — Update (admin) <span class="badge">ADMIN</span></li>
                <li><code>DELETE /api/v1/categories/&lt;id&gt;/</code> — Delete (admin) <span class="badge">ADMIN</span></li>
            </ul>

            <h2>🛍️ Products</h2>
            <ul>
                <li><code>GET /api/v1/products/</code> — List active products (customers), all (admin)</li>
                <li><code>POST /api/v1/products/</code> — Create (admin only) <span class="badge">ADMIN</span></li>
                <li><code>GET /api/v1/products/&lt;id&gt;/</code> — Retrieve</li>
                <li><code>PUT,PATCH /api/v1/products/&lt;id&gt;/</code> — Update (admin) <span class="badge">ADMIN</span></li>
                <li><code>DELETE /api/v1/products/&lt;id&gt;/</code> — Delete (admin) <span class="badge">ADMIN</span></li>
            </ul>

            <h2>🛒 Orders</h2>
            <ul>
                <li><code>POST /api/v1/orders/</code> — Create order (customer only) <span class="badge">CUSTOMER</span></li>
                <li><code>GET /api/v1/orders/</code> — List own orders (customer) or all (admin)</li>
                <li><code>GET /api/v1/orders/&lt;id&gt;/</code> — Retrieve order</li>
                <li><code>POST /api/v1/orders/&lt;id&gt;/cancel/</code> — Cancel pending order (customer) <span class="badge">CUSTOMER</span></li>
                <li><code>POST /api/v1/orders/&lt;id&gt;/change_status/</code> — Update status (admin) <span class="badge">ADMIN</span></li>
            </ul>

            <footer>
                <p>Powered by Django REST Framework • JWT Auth • drf-spectacular</p>
            </footer>
        </div>
    </body>
    </html>
    """
    return HttpResponse(html)


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
