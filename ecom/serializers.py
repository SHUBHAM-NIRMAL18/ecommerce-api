from rest_framework import serializers
from .models import User, Category, Product, Order
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ('username', 'email', 'password')

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)
    
class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['role'] = user.role
        return token


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'description']
        


class ProductSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    category_id = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(),
        source='category',
        write_only=True
    )

    class Meta:
        model = Product
        fields = ['id', 'name', 'price', 'stock', 'is_active', 'category', 'category_id']

    def validate(self, attrs):
        name = attrs.get('name')
        category = attrs.get('category')
        
        if self.instance is None:
            if Product.objects.filter(name=name, category=category).exists():
                raise serializers.ValidationError("Product with this name and category already exists.")
        else:
            if Product.objects.filter(name=name, category=category).exclude(id=self.instance.id).exists():
                raise serializers.ValidationError("Another product with this name and category already exists.")

        return attrs


class ProductInOrderSerializer(serializers.ModelSerializer):
    category = serializers.CharField(source='category.name', read_only=True)

    class Meta:
        model = Product
        fields = ['id', 'name', 'price', 'category']


class OrderWriteSerializer(serializers.ModelSerializer):
    product = serializers.PrimaryKeyRelatedField(queryset=Product.objects.all())
    quantity = serializers.IntegerField()

    class Meta:
        model = Order
        fields = ['product', 'quantity']

    def validate_quantity(self, value):
        if value <= 0:
            raise serializers.ValidationError("Quantity must be at least 1.")
        return value

    def validate(self, data):
        product = data['product']
        qty = data['quantity']

        if not product.is_active:
            raise serializers.ValidationError("Cannot order an inactive product.")

        if product.stock < qty:
            raise serializers.ValidationError(
                f"Only {product.stock} item(s) left in stock, you requested {qty}."
            )

        return data

    def create(self, validated_data):
        order = Order.objects.create(
            customer=self.context['request'].user,
            **validated_data
        )
        product = order.product
        product.stock -= order.quantity
        product.save(update_fields=['stock'])
        return order


class OrderReadSerializer(serializers.ModelSerializer):
    product = ProductInOrderSerializer(read_only=True)
    total_price = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = ['id', 'product', 'quantity', 'status', 'created_at', 'total_price']
        read_only_fields = ['id', 'status', 'created_at', 'total_price']

    def get_total_price(self, obj):
        return obj.quantity * obj.product.price


class OrderChangeStatusSerializer(serializers.Serializer):
    status = serializers.ChoiceField(choices=Order.STATUS_CHOICES)
