from rest_framework import serializers
from .models import Restaurant, Category, Employee, Table, Point, MenuItem, Order, OrderItem, OrderStatusHistory
from users.serializers import UserSerializer

class RestaurantSerializer(serializers.ModelSerializer):
    restaurant = UserSerializer()
    class Meta:
        model = Restaurant
        fields = ["id", "restaurant", "name", "logo", "address", "banner_image", "phone", "description", "time"]

class RestaurantManageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Restaurant
        fields = ["id", "restaurant", "name", "logo", "address", "banner_image", "phone", "description", "time"]

class CategorySerializer(serializers.ModelSerializer):
    restaurant = RestaurantSerializer()
    class Meta:
        model = Category
        fields = ["id", "name", "restaurant"]

class CategoryMangeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["name"]

class EmployeeSerializer(serializers.ModelSerializer):
    restaurant = RestaurantSerializer()
    employee = UserSerializer()
    class Meta:
        model = Employee
        fields = ["id", "name", "employee", "phone", "address", "restaurant", "role"]
        
class EmployeeManageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Employee
        fields = ["id", "name", "employee", "phone", "address", "restaurant", "role"]

class TableSerializer(serializers.ModelSerializer):
    restaurant = RestaurantSerializer()
    class Meta:
        model = Table
        fields = ["id", "restaurant", "number", "qr_code"]

class TableManageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Table
        fields = ["number"]

class PointSerializer(serializers.ModelSerializer):
    class Meta:
        model = Point
        fields = '__all__'

class MenuItemSerializer(serializers.ModelSerializer):
    restaurant = RestaurantSerializer()
    category = CategorySerializer()
    class Meta:
        model = MenuItem
        fields = ["id", "restaurant", "category", "image", "name", "description", "price"]
        
        
class MenuItemManageSerializer(serializers.ModelSerializer):
    class Meta:
        model = MenuItem
        fields = ["id", "category", "image", "name", "description", "price"]


# class OrderCancelSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Order
#         fields = ["status"]

#     def update(self, instance, validated_data):
#         instance.status = "CANCELLED"
#         instance.save()
#         OrderStatusHistory.objects.create(order=instance, status="CANCELLED")
#         return instance


# class OrderItemCancelSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = OrderItem
#         fields = ["id"]

#     def update(self, instance, validated_data):
#         order = instance.order
#         instance.delete()  # Delete the order item

#         # Check if the order has any remaining items
#         if not order.order_items.exists():
#             order.status = "CANCELLED"
#             order.save()
#             OrderStatusHistory.objects.create(order=order, status="CANCELLED")

#         return instance


# Old version 
# # Test Order management 2
# class OrderItemSerializerList2(serializers.ModelSerializer):
#     menu_item = MenuItemSerializer()

#     class Meta:
#         model = OrderItem
#         fields = ["id", "menu_item", "quantity", "employee"]


# class OrderItemSerializer2(serializers.ModelSerializer):
#     class Meta:
#         model = OrderItem
#         fields = ["id", "menu_item", "quantity", "employee"]


# class OrderSerializerList2(serializers.ModelSerializer):
#     order_items = OrderItemSerializerList2(many=True)
#     total_cost = serializers.SerializerMethodField()

#     def get_total_cost(self, obj):
#         return obj.get_total_cost()

#     class Meta:
#         model = Order
#         fields = [
#             "id",
#             "restaurant",
#             "table",
#             "user",
#             "employee",
#             "status",
#             "paid",
#             "timestamp",
#             "order_items",
#             "total_cost",
#         ]


# class OrderSerializer2(serializers.ModelSerializer):
#     order_items = OrderItemSerializer2(many=True)

#     class Meta:
#         model = Order
#         fields = [
#             "id",
#             "restaurant",
#             "table",
#             "user",
#             "employee",
#             "status",
#             "paid",
#             "timestamp",
#             "order_items",
#         ]

#     def create(self, validated_data):
#         order_items_data = validated_data.pop("order_items")
#         order = Order.objects.create(**validated_data)
#         for order_item_data in order_items_data:
#             OrderItem.objects.create(order=order, **order_item_data)
#         return order

#     def update(self, instance, validated_data):
#         order_items_data = validated_data.pop("order_items", None)
#         instance.restaurant = validated_data.get("restaurant", instance.restaurant)
#         instance.table = validated_data.get("table", instance.table)
#         instance.user = validated_data.get("user", instance.user)
#         instance.employee = validated_data.get("employee", instance.employee)
#         instance.status = validated_data.get("status", instance.status)
#         instance.paid = validated_data.get("paid", instance.paid)
#         instance.save()

#         if order_items_data:
#             # Update or create order items
#             for order_item_data in order_items_data:
#                 order_item_id = order_item_data.get("id")
#                 if order_item_id:
#                     order_item = OrderItem.objects.get(id=order_item_id, order=instance)
#                     order_item.menu_item = order_item_data.get(
#                         "menu_item", order_item.menu_item
#                     )
#                     order_item.quantity = order_item_data.get(
#                         "quantity", order_item.quantity
#                     )
#                     order_item.employee = order_item_data.get(
#                         "employee", order_item.employee
#                     )
#                     order_item.save()
#                 else:
#                     OrderItem.objects.create(order=instance, **order_item_data)

#         return instance


# New version

class OrderItemSerializerList2(serializers.ModelSerializer):
    menu_item = MenuItemSerializer()

    class Meta:
        model = OrderItem
        fields = ["id", "menu_item", "quantity", "employee", "status", "created_at", "updated_at"]


class OrderItemSerializer2(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = ["id", "menu_item", "quantity", "employee", "status"]


class OrderSerializerList2(serializers.ModelSerializer):
    order_items = OrderItemSerializerList2(many=True)
    total_cost = serializers.SerializerMethodField()

    def get_total_cost(self, obj):
        return obj.get_total_cost()

    class Meta:
        model = Order
        fields = [
            "id",
            "restaurant",
            "table",
            "user",
            "employee",
            "paid",
            "timestamp",
            "order_items",
            "total_cost",
        ]


class OrderSerializer2(serializers.ModelSerializer):
    order_items = OrderItemSerializer2(many=True)

    class Meta:
        model = Order
        fields = [
            "id",
            "restaurant",
            "table",
            "user",
            "employee",
            "paid",
            "timestamp",
            "order_items",
        ]

    def create(self, validated_data):
        order_items_data = validated_data.pop("order_items")
        order = Order.objects.create(**validated_data)
        for order_item_data in order_items_data:
            order_item = OrderItem.objects.create(order=order, **order_item_data)
            OrderStatusHistory.objects.create(order_item=order_item, status=order_item.status)
        return order

    def update(self, instance, validated_data):
        order_items_data = validated_data.pop("order_items", None)
        instance.restaurant = validated_data.get("restaurant", instance.restaurant)
        instance.table = validated_data.get("table", instance.table)
        instance.user = validated_data.get("user", instance.user)
        instance.employee = validated_data.get("employee", instance.employee)
        instance.paid = validated_data.get("paid", instance.paid)
        instance.save()

        if order_items_data:
            # Update or create order items
            for order_item_data in order_items_data:
                order_item_id = order_item_data.get("id")
                if order_item_id:
                    order_item = OrderItem.objects.get(id=order_item_id, order=instance)
                    order_item.menu_item = order_item_data.get(
                        "menu_item", order_item.menu_item
                    )
                    order_item.quantity = order_item_data.get(
                        "quantity", order_item.quantity
                    )
                    order_item.employee = order_item_data.get(
                        "employee", order_item.employee
                    )
                    order_item.status = order_item_data.get(
                        "status", order_item.status
                    )
                    order_item.save()
                else:
                    order_item = OrderItem.objects.create(order=instance, **order_item_data)
                OrderStatusHistory.objects.create(order_item=order_item, status=order_item.status)

        return instance
    
class OrderItemStatusUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = ["status"]  # Only the status field will be updated
        
class TableSerializer2(serializers.ModelSerializer):
    orders = serializers.SerializerMethodField()
    pending_order_items_count = serializers.SerializerMethodField()

    class Meta:
        model = Table
        fields = ['id', 'number', 'qr_code', 'orders', "pending_order_items_count"]

    def get_orders(self, obj):
        orders = obj.orders.filter(order_items__status__in=["PENDING", "PREPARING"]).distinct()
        return OrderSerializer2(orders, many=True).data
    
    def get_pending_order_items_count(self, obj):
        return OrderItem.objects.filter(order__table=obj, status="PENDING").count()
        
        