import math
from rest_framework import serializers
from rest_framework.serializers import ValidationError
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from store.models import (
    StoreModel,
    GoodsModel,
    ReviewModel,
    OrderModel,
    ImageModel,
    SizeModel,
    ColorModel,
    CategoryModel,
    ProductImage,
    Order,
    OrderItem,
    BankAccount,
    Review,
    WebInfo,
    NoticeModel,
    HotelQR
)
from users.models import UserModel

from users.serializers import UserSerializer


def format_with_commas(n):
    return "{:,}".format(int(n))


class CategorySerializer(serializers.ModelSerializer):
    sorted_ID = serializers.IntegerField(required=False)

    class Meta:
        model = CategoryModel
        fields = ("id", "name", "image", "sorted_ID")
        ordering = ["sorted_ID"]  # เพิ่มการจัดเรียงจากน้อยไปมาก



class GoodsSerializer(serializers.ModelSerializer):
    store_name = serializers.SerializerMethodField()
    star_avg = serializers.SerializerMethodField()
    # category = serializers.SerializerMethodField()
    format_price = serializers.SerializerMethodField()
    review_total = serializers.SerializerMethodField()
    store_address = serializers.SerializerMethodField()
    sizes = serializers.SerializerMethodField()
    colors = serializers.SerializerMethodField()
    image = serializers.SerializerMethodField()
    images = serializers.SerializerMethodField()

    def get_store_name(self, obj):
        store_name = obj.store.name
        if len(store_name) >= 7:
            store_name = f"{store_name[:7]}..."
        return store_name

    def get_star_avg(self, obj):
        review = Review.objects.filter(product_id=obj.id).values("rating")
        total = 0
        for i in review:
            total += i["rating"]

        return math.ceil(total / review.count()) if total != 0 else 0

    # def get_category(self, obj):
    #     return obj.category.name

    def get_format_price(self, obj):
        return str(format_with_commas(obj.price))

    def get_review_total(self, obj):
        # review_total = ReviewModel.objects.filter(goods_id=obj.id).count()
        review_total = Review.objects.filter(product_id=obj.id).count()
        return review_total

    def get_store_address(self, obj):
        address = obj.store.address.split(" ")[:2]
        address = " ".join(address)
        return address

    def get_sizes(self, obj):
        sizes = SizeModel.objects.filter(product=obj)
        serializer = SizeSerializer(sizes, many=True)
        return serializer.data

    def get_colors(self, obj):
        colors = ColorModel.objects.filter(product=obj)
        serializer = ColorSerializer(colors, many=True)
        return serializer.data

    def get_image(self, obj):
        image = ImageModel.objects.filter(goods_id=obj.id).first()
        serializer = ImageSerializer(image)
        image = serializer.data.get("image")
        return image

    def get_images(self, obj):
        images = ProductImage.objects.filter(product=obj).first()
        serializer = ProductImageSerializer(images)
        images = serializer.data.get("image")
        return images

    class Meta:
        model = GoodsModel
        exclude = ["created_at", "updated_at"]
        # extra_kwargs = {
        #     "category": {"required": False},
        # }


class UpdateStoreSerializer(serializers.ModelSerializer):
    def validate(self, attrs):
        name = attrs.get("name")
        if name:
            if len(name) > 15:
                raise ValidationError(
                    "Please write your store name in 15 characters or less."
                )
        return attrs

    class Meta:
        model = StoreModel
        fields = "__all__"
        extra_kwargs = {
            "seller": {"required": False},
        }


class OnlyStoreInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = StoreModel
        exclude = ["seller"]


class StoreSerializer(serializers.ModelSerializer):
    goods_set = serializers.SerializerMethodField()
    seller = UserSerializer()

    def get_seller(self, obj):
        return obj.seller.email

    def get_goods_set(self, obj):
        goods = GoodsModel.objects.filter(store_id=obj.id)
        serializer = OnlyStoreGoodsSerializer(goods, many=True)
        return serializer.data

    class Meta:
        model = StoreModel
        fields = "__all__"


# new review
class ReviewSerializer(serializers.ModelSerializer):
    user = UserSerializer()
    class Meta:
        model = Review
        fields = "__all__"


class ReviewCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = "__all__"


class GoodsDetailSerializer(serializers.ModelSerializer):
    """
    Replace store with name
    Create a review set for the product
    """

    store_name = serializers.SerializerMethodField()
    store_user_id = serializers.SerializerMethodField()
    review_set = serializers.SerializerMethodField()
    category = serializers.SerializerMethodField()
    sizes = serializers.SerializerMethodField()
    colors = serializers.SerializerMethodField()
    image_set = serializers.SerializerMethodField()
    images = serializers.SerializerMethodField()
    address = serializers.SerializerMethodField()
    price = serializers.SerializerMethodField()
    format_price = serializers.SerializerMethodField()
    star_avg = serializers.SerializerMethodField()
    store_image = serializers.SerializerMethodField()
    store_id = serializers.SerializerMethodField()

    def get_store_name(self, obj):
        return obj.store.name

    def get_store_id(self, obj):
        return obj.store.id

    def get_review_set(self, obj):
        # review = ReviewModel.objects.filter(goods_id=obj.id).order_by("-created_at")
        review = Review.objects.filter(product_id=obj.id).order_by("-created_at")
        serializer = ReviewSerializer(review, many=True)
        return serializer.data

    def get_category(self, obj):
        return obj.category.name

    def get_sizes(self, obj):
        sizes = SizeModel.objects.filter(product=obj)
        serializer = SizeSerializer(sizes, many=True)
        return serializer.data

    def get_colors(self, obj):
        colors = ColorModel.objects.filter(product=obj)
        serializer = ColorSerializer(colors, many=True)
        return serializer.data

    def get_image_set(self, obj):
        images = ProductImage.objects.filter(product_id=obj.id)
        serializer = ProductImageSerializer(images, many=True)
        image_set = [i["image"] for i in serializer.data]
        return image_set

    def get_images(self, obj):
        images = ProductImage.objects.filter(product=obj).first()
        serializer = ProductImageSerializer(images)
        images = serializer.data.get("image")
        return images

    def get_address(self, obj):
        address = obj.store.address
        # address = obj.store.address.split(' ')[:2]
        # address = ' '.join(address)
        return address

    def get_store_user_id(self, obj):
        return obj.store.seller.id

    # def get_price(self, obj):
    #     return str(format_with_commas(obj.price))

    def get_price(self, obj):
        return obj.price

    def get_store_image(self, obj):
        return (
            obj.store.seller.profile_image.url
            if obj.store.seller.profile_image
            else False
        )

    def get_star_avg(self, obj):
        review = Review.objects.filter(product_id=obj.id).values("rating")
        total = 0
        for i in review:
            total += i["rating"]

        return math.ceil(total / review.count()) if total != 0 else 0

    def get_format_price(self, obj):
        return str(format_with_commas(obj.price))

    class Meta:
        model = GoodsModel
        exclude = ["created_at", "updated_at"]


class SizeSerializer(serializers.ModelSerializer):
    class Meta:
        model = SizeModel
        fields = "__all__"


class ColorSerializer(serializers.ModelSerializer):
    class Meta:
        model = ColorModel
        fields = "__all__"


class ImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ImageModel
        fields = "__all__"
        extra_kwargs = {
            "goods": {"required": False},
        }


class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = "__all__"


# Order
class OrderItemSerializer(serializers.ModelSerializer):
    product = GoodsSerializer()

    class Meta:
        model = OrderItem
        fields = ["id", "product", "quantity", "price", "color", "size"]


class OrderSerializer(serializers.ModelSerializer):
    items = serializers.SerializerMethodField()
    user = UserSerializer()

    def get_items(self, obj):
        order_items = OrderItem.objects.filter(order=obj)
        serializer = OrderItemSerializer(order_items, many=True)
        return serializer.data

    class Meta:
        model = Order
        fields = [
            "id",
            "user",
            "store",
            "tel",
            "total_prices",
            "account_name",
            "province",
            "district",
            "shipping_company",
            "branch",
            "created_at",
            "status",
            "items",
            "china_url",
            "lao_url",
            "order_bill",
        ]


class OrderItemCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = ["id", "product", "quantity", "price", "color", "size"]


class OrderCreateSerializer(serializers.ModelSerializer):
    items = OrderItemCreateSerializer(many=True, write_only=True)
    user = serializers.PrimaryKeyRelatedField(queryset=UserModel.objects.all(), required=False, allow_null=True)


    def create(self, validated_data):
        order_items_data = validated_data.pop("items")
        order = Order.objects.create(**validated_data)
        total_prices = 0
        for order_item_data in order_items_data:
            product = order_item_data['product']
            quantity = order_item_data['quantity']
            

                 # ตรวจสอบหมวดหมู่ของสินค้า
            if product.category.id in [46, 64]:

                if product.quantity > 0:
                    if quantity > product.quantity:
                        quantity_to_reduce = product.quantity
                    else:
                        quantity_to_reduce = quantity
                    product.quantity -= quantity_to_reduce
                    product.save()
            else:
                # สำหรับสินค้าอื่นๆ ตรวจสอบและลดจำนวนตามปกติ
                if product.quantity < quantity:
                    raise ValidationError(f"Product '{product.name}' Not enough, in stock {product.quantity} piece but want to order {quantity} item")
                product.quantity -= quantity
                product.save()


            
            order_item = OrderItem.objects.create(order=order, **order_item_data)
            total_prices += order_item.price * order_item.quantity

        order.total_prices = total_prices
        order.save()
        return order

    class Meta:
        model = Order
        fields = [
            "id",
            "user",
            "store",
            "tel",
            "total_prices",
            "account_name",
            "province",
            "district",
            "shipping_company",
            "branch",
            "created_at",
            "status",
            "items",
        ]

# -----------
class OrderItemCreateSerializer2(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = ["product", "quantity", "price", "color", "size"]

class OrderCreateSerializer2(serializers.ModelSerializer):
    items = OrderItemCreateSerializer(many=True, write_only=True)
    user = serializers.PrimaryKeyRelatedField(queryset=UserModel.objects.all(), required=False, allow_null=True)

    class Meta:
        model = Order
        fields = [
            "user",
            "store",
            "tel",
            "total_prices",
            "account_name",
            "province",
            "district",
            "shipping_company",
            "branch",
            "status",
            "items",
        ]

    def validate(self, data):
        items = data.get('items')
        if not items:
            raise serializers.ValidationError("At least one order item is required.")
        if data.get('total_prices') <= 0:
            raise serializers.ValidationError("Total prices must be greater than zero.")
        # Additional validations as needed
        return data

    def create(self, validated_data):
        items_data = validated_data.pop('items')
        # Do not handle 'user' field here
        order = Order.objects.create(**validated_data)
        order_items = [OrderItem(order=order, **item) for item in items_data]
        OrderItem.objects.bulk_create(order_items)
        return order
# -----------  

class PendingOrderSerializer(OrderSerializer):
    class Meta:
        model = Order
        fields = [
            "id",
            "user",
            "store",
            "tel",
            "total_prices",
            "account_name",
            "province",
            "district",
            "shipping_company",
            "branch",
            "created_at",
            "status",
            "items",
        ]

    def to_representation(self, instance):
        data = super().to_representation(instance)
        if instance.status != "Pending":
            return None  # Skip orders that are not pending
        return data


class ProcessingOrderSerializer(OrderSerializer):
    class Meta:
        model = Order
        fields = [
            "id",
            "user",
            "store",
            "tel",
            "total_prices",
            "account_name",
            "province",
            "district",
            "shipping_company",
            "branch",
            "created_at",
            "status",
            "items",
        ]

    def to_representation(self, instance):
        data = super().to_representation(instance)
        if instance.status != "Processing":
            return None  # Skip orders that are not processing
        return data


class DeliveredOrderSerializer(OrderSerializer):
    items = OrderItemSerializer(source='orderitem_set', many=True)
    class Meta:
        model = Order
        fields = [
            "id",
            "user",
            "store",
            "tel",
            "total_prices",
            "account_name",
            "province",
            "district",
            "shipping_company",
            "branch",
            "created_at",
            "status",
            "items",
        ]

    def to_representation(self, instance):
        data = super().to_representation(instance)
        if instance.status != "Delivered":
            return None  # Skip orders that are not Delivered
        return data


class ShippedOrderSerializer(OrderSerializer):
    class Meta:
        model = Order
        fields = [
            "id",
            "user",
            "store",
            "tel",
            "total_prices",
            "account_name",
            "province",
            "district",
            "shipping_company",
            "branch",
            "created_at",
            "status",
            "items",
        ]

    def to_representation(self, instance):
        data = super().to_representation(instance)
        if instance.status != "Shipped":
            return None  # Skip orders that are not Shipped
        return data


class OrderItemUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = ["product", "quantity", "color", "size"]


class OrderUpdateSerializer(serializers.ModelSerializer):
    def update(self, instance, validated_data):
        # Update order fields
        instance.status = validated_data.get("status", instance.status)
        instance.save()

        return instance

    class Meta:
        model = Order
        fields = ["status"]
        
class OrderUpdateSerializer2(serializers.ModelSerializer):
    def update(self, instance, validated_data):
        # Update order fields
        instance.created_at = validated_data.get("created_at", instance.created_at)
        instance.save()

        return instance

    class Meta:
        model = Order
        fields = ["created_at"]


class OrderUpdateChinaUrlSerializer(serializers.ModelSerializer):
    def update(self, instance, validated_data):
        # Update order fields
        instance.china_url = validated_data.get("china_url", instance.china_url)
        instance.save()

        return instance

    class Meta:
        model = Order
        fields = ["china_url"]


class OrderUpdateLaoUrlSerializer(serializers.ModelSerializer):
    def update(self, instance, validated_data):
        # Update order fields
        instance.lao_url = validated_data.get("lao_url", instance.lao_url)
        instance.save()

        return instance

    class Meta:
        model = Order
        fields = ["lao_url"]


class OrderUpdateBillSerializer(serializers.ModelSerializer):
    def update(self, instance, validated_data):
        # Update order fields
        instance.order_bill = validated_data.get("order_bill", instance.order_bill)
        instance.save()

        return instance

    class Meta:
        model = Order
        fields = ["order_bill"]


class PostSerializer(serializers.Serializer):
    name = serializers.CharField(help_text="product name")
    price = serializers.IntegerField(help_text="product price")

    review = serializers.CharField(help_text="Review contents")

    search = serializers.CharField(help_text="What to search for")

    goods_id = serializers.IntegerField(help_text="Product ID to order")


class OnlyStoreGoodsSerializer(serializers.ModelSerializer):
    """
    Replace store with name
    Create a review set for the product
    """

    review_set = serializers.SerializerMethodField()
    # category = serializers.SerializerMethodField()
    order_set = serializers.SerializerMethodField()
    goods_id = serializers.SerializerMethodField()
    image_set = serializers.SerializerMethodField()
    images = serializers.SerializerMethodField()
    format_price = serializers.SerializerMethodField()
    star_avg = serializers.SerializerMethodField()

    def get_store(self, obj):
        return obj.store.name

    def get_review_set(self, obj):
        # review = ReviewModel.objects.filter(goods_id=obj.id).order_by("-created_at")
        review = Review.objects.filter(product_id=obj.id).order_by("-created_at")
        serializer = OnlyStoreReviewSerializer(review, many=True)
        return serializer.data

    # def get_category(self, obj):
    #     return obj.category.name

    def get_order_set(self, obj):
        order = OrderModel.objects.filter(goods_id=obj.id).order_by("-ordered_at")
        serializer = OrderSerializer(order, many=True)
        return serializer.data

    def get_goods_id(self, obj):
        return obj.id

    def get_image_set(self, obj):
        images = ProductImage.objects.filter(product_id=obj.id)
        serializer = ProductImageSerializer(images, many=True)
        image_set = [i["image"] for i in serializer.data]
        return image_set

    def get_images(self, obj):
        images = ProductImage.objects.filter(product=obj).first()
        serializer = ProductImageSerializer(images)
        images = serializer.data.get("image")
        return images

    def get_format_price(self, obj):
        return str(format_with_commas(obj.price))

    def get_star_avg(self, obj):
        review = Review.objects.filter(product_id=obj.id).values("rating")
        total = 0
        for i in review:
            total += i["rating"]

        return math.ceil(total / review.count()) if total != 0 else 0

    class Meta:
        model = GoodsModel
        fields = [
            "star_avg",
            "goods_id",
            "review_set",
            "category",
            "order_set",
            "name",
            "price",
            "quantity",
            "format_price",
            "image_set",
            "images",
            "description",
        ]


class OnlyStoreReviewSerializer(serializers.ModelSerializer):
    review_id = serializers.SerializerMethodField()
    user_name = serializers.SerializerMethodField()
    goods_id = serializers.SerializerMethodField()
    created_at = serializers.SerializerMethodField()
    user_profile = serializers.SerializerMethodField()

    def get_review_id(self, obj):
        return obj.id

    def get_user_name(self, obj):
        return obj.user.nickname

    def get_goods_id(self, obj):
        return obj.id

    def get_created_at(self, obj):
        return obj.created_at.strftime("%Y.%m.%d")

    def get_user_profile(self, obj):
        return obj.user.profile_image.url if obj.user.profile_image else None

    class Meta:
        model = Review
        exclude = ["updated_at", "product", "id"]
        extra_kwargs = {
            "user": {"required": False},
            "product": {"required": False},
        }


class ChatStoreSerializer(serializers.Serializer):
    class Meta:
        model = StoreModel
        exclude = ["created_at", "updated_at"]


class GoodsCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = GoodsModel
        exclude = ["store", "category"]
        # extra_kwargs = {
        #     "description": {"required": False},
        # }


class CreateProductSerializer(serializers.ModelSerializer):
    sizes = serializers.ListField(
        child=serializers.CharField(max_length=50), required=False
    )
    colors = serializers.ListField(
        child=serializers.CharField(max_length=50), required=False
    )
    images = serializers.ListField(child=serializers.ImageField(), required=False)

    class Meta:
        model = GoodsModel
        fields = [
            "name",
            "description",
            "price",
            "quantity",
            "category",
            "store",
            "sizes",
            "colors",
            "images",
        ]

    def create(self, validated_data):
        sizes_data = validated_data.pop("sizes", [])
        colors_data = validated_data.pop("colors", [])
        images_data = validated_data.pop("images", [])

        product = GoodsModel.objects.create(**validated_data)

        for size_name in sizes_data:
            size = SizeModel.objects.create(product=product, name=size_name)

        for color_name in colors_data:
            color = ColorModel.objects.create(product=product, name=color_name)

        for image_file in images_data:
            image = ProductImage.objects.create(product=product, image=image_file)

        return product

    def to_representation(self, instance):
        representation = super().to_representation(instance)

        sizes = instance.size_set.all()
        colors = instance.color_set.all()
        images = instance.images.all()

        representation["sizes"] = SizeSerializer(sizes, many=True).data
        representation["colors"] = ColorSerializer(colors, many=True).data
        representation["images"] = ProductImageSerializer(images, many=True).data

        return representation


# class UpdateProductSerializer(serializers.ModelSerializer):
#     sizes = serializers.ListField(child=serializers.CharField(max_length=50), required=False)
#     colors = serializers.ListField(child=serializers.CharField(max_length=50), required=False)
#     images = serializers.ListField(child=serializers.ImageField(), required=False)

#     class Meta:
#         model = GoodsModel
#         fields = ['name', 'description', 'price', 'category', 'sizes', 'colors', 'images']

#     def update(self, instance, validated_data):
#         sizes_data = validated_data.pop('sizes', None)
#         colors_data = validated_data.pop('colors', None)
#         images_data = validated_data.pop('images', None)

#         for attr, value in validated_data.items():
#             setattr(instance, attr, value)

#         instance.save()

#         if sizes_data is not None:
#             instance.size.all().delete()  # Clear existing sizes
#             for size_name in sizes_data:
#                 SizeModel.objects.create(product=instance, name=size_name)

#         if colors_data is not None:
#             instance.color.all().delete()  # Clear existing colors
#             for color_name in colors_data:
#                 ColorModel.objects.create(product=instance, name=color_name)

#         if images_data is not None:
#             instance.images.all().delete()  # Clear existing images
#             for image_file in images_data:
#                 ProductImage.objects.create(product=instance, image=image_file)

#         return instance


class UpdateProductSerializer(serializers.ModelSerializer):
    sizes = serializers.ListField(
        child=serializers.CharField(max_length=50), required=False
    )
    colors = serializers.ListField(
        child=serializers.CharField(max_length=50), required=False
    )
    images = serializers.ListField(child=serializers.ImageField(), required=False)

    class Meta:
        model = GoodsModel
        fields = [
            "name",
            "description",
            "price",
            "quantity",
            "category",
            "sizes",
            "colors",
            "images",
        ]

    def update(self, instance, validated_data):
        sizes_data = validated_data.pop("sizes", None)
        colors_data = validated_data.pop("colors", None)
        images_data = validated_data.pop("images", None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()

        if sizes_data is not None:
            instance.size.all().delete()  # Clear existing sizes
            for size_name in sizes_data:
                SizeModel.objects.create(product=instance, name=size_name)

        if colors_data is not None:
            instance.color.all().delete()  # Clear existing colors
            for color_name in colors_data:
                ColorModel.objects.create(product=instance, name=color_name)

        if images_data is not None:
            instance.images.all().delete()  # Clear existing images
            for image_file in images_data:
                ProductImage.objects.create(product=instance, image=image_file)

        return instance


# bank account
class BankAccountSerializer(serializers.ModelSerializer):
    # Assuming 'store' is a ForeignKey field in your BankAccount model

    # Use PrimaryKeyRelatedField if store is represented by its ID
    store = serializers.PrimaryKeyRelatedField(queryset=StoreModel.objects.all())

    class Meta:
        model = BankAccount
        fields = ["id", "name", "account_name", "account_number", "image1","image2", "store"]


class BankAccountSerializer2(serializers.ModelSerializer):
    class Meta:
        model = BankAccount
        fields = "__all__"


class BankAccountByStoreSerializer(serializers.Serializer):
    has_bank_account = serializers.SerializerMethodField()

    def get_has_bank_account(self, obj):
        return obj


# class BankAccountDetailByStoreSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = BankAccount
#         fields = ['id', 'name', 'account_name', 'account_number', 'image']


class WebInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = WebInfo
        fields = [
            "id",
            "name",
            "tel1",
            "tel2",
            "email",
            "address",
            "description",
            "logo",
            "banner1",
            "banner2",
            "banner3",
            "message",
        ]

class WebInfoLogoSerializer(serializers.ModelSerializer):
    class Meta:
        model = WebInfo
        fields = [
            "logo"
        ]
        
class WebInfoBannerSerializer(serializers.ModelSerializer):
    class Meta:
        model = WebInfo
        fields = [
            "banner1"
        ]


class NoticeListSerializers(serializers.ModelSerializer):
    user = UserSerializer()

    class Meta:
        model = NoticeModel
        fields = ["id", "subject", "user", "brochure", "created_at", "updated_at"]


class NoticeSerializers(serializers.ModelSerializer):
    class Meta:
        model = NoticeModel
        fields = ["id", "subject", "user", "brochure"]

class HotelQRSerializers(serializers.ModelSerializer):
    class Meta:
        model = HotelQR
        fields = ["id", "hotel", "room_number", "address", "qr_code"]