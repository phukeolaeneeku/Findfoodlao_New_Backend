from rest_framework import serializers
from rest_framework.serializers import ValidationError
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from users.models import UserModel
from store.models import StoreModel
from restaurant2.models import Restaurant, Employee


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserModel
        fields = "__all__"

    def validate(self, attrs):
        if attrs:
            nickname = attrs.get("nickname")
            if nickname:
                if len(nickname) > 10:
                    raise ValidationError(
                        "Please write your nickname in 10 characters or less."
                    )
            if len(attrs.get("password")) < 8:
                raise ValidationError(
                    "Please write your password with at least 8 characters."
                )
        return attrs

    def create(self, validated_data):
        user = super().create(validated_data)
        password = user.password
        user.set_password(password)
        user.save()
        return user

    def update(self, instance, validated_data):
        print(33)
        password = validated_data.get("password")  # Get password value
        if password:  # Run only if password value exists
            user = super().update(instance, validated_data)
            user.set_password(password)
            user.save()
        elif not password:
            return instance
        else:
            user = super().update(instance, validated_data)
            user.save()
        return instance


class AdminUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserModel
        fields = ["id", "email", "nickname", "profile_image"]


class ClientUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserModel
        fields = ["id", "email", "nickname", "profile_image"]


class SellerUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserModel
        fields = ["id", "email", "nickname", "profile_image"]


class GetUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserModel
        exclude = ["password", "is_active", "last_login"]


class LoginSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token["email"] = user.email
        token["user_id"] = user.id
        token["is_admin"] = user.is_admin

        return token


class SellerSerializer(serializers.ModelSerializer):
    def validate(self, attrs):
        name = attrs.get("name")
        phone = attrs.get("phone")
        introduce = attrs.get("introduce")
        if name:
            if len(name) > 15:
                raise ValidationError(
                    "Please write your store name in 15 characters or less."
                )
        if phone:
            if not phone.isdigit():
                raise ValidationError(
                    "Please enter only numbers for your phone number!"
                )
        if introduce:
            if len(introduce) > 300:
                raise ValidationError(
                    "Please write your introduction in 300 characters or less."
                )
        return attrs

    class Meta:
        model = StoreModel
        fields = "__all__"

        extra_kwargs = {
            "seller": {"required": False},
            "name": {"required": True},
            "address": {"required": True},
        }


# Management Restaurant
class RestaurantSerializer(serializers.ModelSerializer):
    class Meta:
        model = Restaurant
        fields = "__all__"

        extra_kwargs = {
            "restaurant": {"required": False},
            "name": {"required": True},
            "address": {"required": True},
        }
        
class EmployeeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Employee
        fields = "__all__"

        extra_kwargs = {
            "restaurant": {"required": False},
            "employee": {"required": False},
            "phone": {"required": True},
            "address": {"required": True},
        }


class PostUserSerializer(serializers.Serializer):
    email = serializers.CharField(help_text="email")
    code = serializers.CharField(help_text="Authentication code")
    new_password = serializers.CharField(help_text="change password")
    origin_password = serializers.CharField(help_text="original password")
    password = serializers.CharField(help_text="Password required for login")
    password2 = serializers.CharField(help_text="Password check")
    social = serializers.CharField(help_text="Types for social login transfer URLs")
