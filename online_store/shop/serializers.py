from rest_framework import serializers
from .models import *
from django.contrib.auth.models import User
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate


class UserSerializers(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ("username", "email", "password", "first_name", "last_name", "age",
                  "date_registered", "phone_number", "status")
        extra_kwargs = {"password": {"write_only": True}}

    def create(self, validated_data):
        user = UserProfile.objects.create_user(**validated_data)
        return user

    def to_representation(self, instance):
        refresh = RefreshToken.for_user(instance)
        return {
            "user": {
                "username": instance.username,
                "email": instance.email,
            },
            'access': str(refresh.access_token),
            "refresh": str(refresh),
        }


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only= True)

    def validate(self, data):
        user = authenticate(**data)
        if user and user.is_active:
            return user
        raise serializers.ValidationError("Неверные учетные данные")

    # def to_representation(self, instance):
    #     refresh = RefreshToken.for_user(instance)
    #     return {
    #         "user": {
    #             "username": instance.username,
    #             "email": instance.email,
    #         },
    #         'access': str(refresh.access_token),
    #         "refresh": str(refresh),
    #     }


class UserProfileSerializers(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = "__all__"


class UserProfileSimpleSerializers(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ["first_name", "last_name"]



class CategorySerializers(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["category_name"]


class ProductPhotosSerializers(serializers.ModelSerializer):
    class Meta:
        model = ProductPhotos
        fields = ["product"]


class RatingSerializers(serializers.ModelSerializer):
    class Meta:
        model = Rating
        fields = "__all__"


class ReviewSerializers(serializers.ModelSerializer):
    created_date = serializers.DateTimeField(format="%d-%m-%Y %H:%M")
    class Meta:
        model = Review
        fields = "__all__"


class ProductListSerializers(serializers.ModelSerializer):
    date = serializers.DateField(format="%d-%m-%Y")
    average_rating = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = ["product_name", "price", "active", "average_rating", "date"]


    def get_average_rating(self, obj):
        return obj.get_average_rating()


class ProductDetailSerializers(serializers.ModelSerializer):
    category = CategorySerializers()
    ratings = RatingSerializers(read_only=True, many=True)
    review = ReviewSerializers(read_only=True, many=True)
    product = ProductPhotosSerializers(read_only=True, many=True)
    date = serializers.DateField(format="%d-%m-%Y")
    average_rating = serializers.SerializerMethodField()
    owner = UserProfileSimpleSerializers()

    class Meta:
        model = Product
        fields = ["product_name", "category", "description", "price", "product",
                  "product_video", "active", "average_rating", "ratings", "review", "date", "owner"]


    def get_average_rating(self, obj):
        return obj.get_average_rating()


class CartItemSerializer(serializers.ModelSerializer):
    product = ProductListSerializers(read_only=True)
    product_id = serializers.PrimaryKeyRelatedField(queryset=Product.objects.all(), write_only=True, source="product")


    class Meta:
        model = CartItem
        fields = ["id", "product", "product_id", "quantity", "get_total_item_price"]


class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)
    total_price = serializers.SerializerMethodField()

    class Meta:
        model = Cart
        fields = ["id", "user", "items", "total_price"]


    def get_total_price(self, obj):
        return obj.get_total_price()