import math
from rest_framework import serializers
from rest_framework.serializers import ValidationError
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from chat.models import MessageModel, RoomModel
from store.models import StoreModel, GoodsModel, ReviewModel, OrderModel, ImageModel
from users.models import UserModel


class ChatSerializer(serializers.ModelSerializer):
    store_name = serializers.SerializerMethodField()
    last_message = serializers.SerializerMethodField()
    user_name = serializers.SerializerMethodField()
    user_profile = serializers.SerializerMethodField()
    store_image = serializers.SerializerMethodField()

    def get_store_name(self, obj):
        store_name = obj.store.name
        if len(store_name) >= 7:
            store_name = f"{store_name[:7]}..."
        return store_name

    def get_last_message(self, obj):
        message = MessageModel.objects.filter(room_id=obj.id).last()
        serializer = MessageSerializer(message)
        return serializer.data.get('message')[:15] + '...'

    def get_user_name(self, obj):
        if obj.user:
            user_name = obj.user.nickname
        else:
            user_name = '(User who withdrew)'
        return user_name

    def get_user_profile(self, obj):
        if not obj.user:
            return False
        return obj.user.profile_image.url if obj.user.profile_image else False


    def get_store_image(self, obj):
        return obj.store.seller.profile_image.url if obj.store.seller.profile_image else False


    class Meta:
        model = RoomModel
        exclude = ["updated_at", ]


class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = MessageModel
        fields = "__all__"
