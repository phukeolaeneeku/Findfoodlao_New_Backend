import base64
import uuid
from collections import Counter
from pprint import pprint
from PIL import Image
import io
import django
from django.core.files.base import ContentFile
from django.db.models import Q, Count
from django.shortcuts import render, redirect
from django.contrib import messages
from rest_framework import status, permissions, generics, viewsets, response, filters
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import BasePermission
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.generics import CreateAPIView
from django.http import JsonResponse
from rest_framework.viewsets import ModelViewSet
from rest_framework.filters import OrderingFilter
from django.http import Http404
from datetime import datetime, timedelta
from django.utils import timezone
from django.db.models import Q
import openpyxl
from openpyxl import Workbook
from django.http import HttpResponse

from .form import ReviewForm
from .models import (
    GoodsModel,
    StoreModel,
    ReviewModel,
    BookmarkModel,
    OrderModel,
    FilteringModel,
    ImageModel,
    CategoryModel,
    PolicyModel,
    SizeModel,
    ColorModel,
    ProductImage,
    Order,
    OrderItem,
    BankAccount,
    Review,
    WebInfo,
    NoticeModel,
    HotelQR
)
from .serializers import (
    StoreSerializer,
    GoodsSerializer,
    ReviewSerializer,
    GoodsDetailSerializer,
    OrderSerializer,
    OrderCreateSerializer,
    OrderUpdateSerializer,
    PendingOrderSerializer,
    ProcessingOrderSerializer,
    ShippedOrderSerializer,
    DeliveredOrderSerializer,
    OrderUpdateChinaUrlSerializer,
    OrderUpdateLaoUrlSerializer,
    OrderUpdateBillSerializer,
    PostSerializer,
    UpdateStoreSerializer,
    ImageSerializer,
    GoodsCreateSerializer,
    CategorySerializer,
    CreateProductSerializer,
    UpdateProductSerializer,
    BankAccountSerializer,
    BankAccountSerializer2,
    ReviewCreateSerializer,
    WebInfoSerializer,
    NoticeListSerializers,
    NoticeSerializers,
    HotelQRSerializers
)

from .permissions import IsOwnerOrReadOnly

from drf_yasg.utils import swagger_auto_schema

"""
Permission to divide general users, merchants, and administrators
"""


class IsSeller(BasePermission):
    def has_permission(self, request, view):
        try:
            seller = request.user.is_seller
            admin = request.user.is_admin
            if seller or admin:
                return True
            else:
                return False
        except:
            # Login
            return False


def goods_list(request):
    goods_by_category = GoodsModel.objects.values('category__name').annotate(products=Count('id')).order_by('category__name')

    context = {
        'goods_by_category': goods_by_category,
    }
    return render(request, 'store/goods_list.html', context)


def goods_detail(request, goods_id):
    return render(request, "store/goods_detail.html")


def order_list(request):
    return render(request, "store/order_list.html")


def store_setting(request):
    return render(request, "store/admin.html")


# Notice management
# class NoticeList(generics.ListAPIView):
#     queryset = NoticeModel.objects.all()
#     serializer_class = NoticeListSerializers

# class NoticeDetailDelete(generics.RetrieveDestroyAPIView):
#     queryset = NoticeModel.objects.all()
#     serializer_class = NoticeListSerializers

# class NoticeCreate(generics.CreateAPIView):
#     queryset = NoticeModel.objects.all()
#     serializer_class = NoticeSerializers

# class NoticeUpdate(generics.UpdateAPIView):
#     queryset = NoticeModel.objects.all()
#     serializer_class = NoticeSerializers


class NoticeList(generics.ListAPIView):
    queryset = NoticeModel.objects.all()
    serializer_class = NoticeListSerializers


class NoticeDetailDelete(generics.RetrieveDestroyAPIView):
    queryset = NoticeModel.objects.all()
    serializer_class = NoticeListSerializers

    def delete(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        messages.success(request, "Notice deleted successfully.")
        return Response(
            {"message": "Notice deleted successfully."},
            status=status.HTTP_200_OK,
        )


class NoticeCreate(generics.CreateAPIView):
    queryset = NoticeModel.objects.all()
    serializer_class = NoticeSerializers

    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        if response.status_code == status.HTTP_201_CREATED:
            messages.success(request, "Notice created successfully.")
            return Response(
                {"message": "Notice created successfully.", "data": response.data},
                status=status.HTTP_201_CREATED,
            )
        else:
            return Response(
                {"message": "Error creating notice.", "errors": response.data},
                status=response.status_code,
            )


class NoticeUpdate(generics.UpdateAPIView):
    queryset = NoticeModel.objects.all()
    serializer_class = NoticeSerializers

    def update(self, request, *args, **kwargs):
        response = super().update(request, *args, **kwargs)
        if response.status_code == status.HTTP_200_OK:
            messages.success(request, "Notice updated successfully.")
            return Response(
                {"message": "Notice updated successfully.", "data": response.data},
                status=status.HTTP_200_OK,
            )
        else:
            return Response(
                {"message": "Error updating notice.", "errors": response.data},
                status=response.status_code,
            )


# Category management
class CategoryListCreate(generics.ListCreateAPIView):
    queryset = CategoryModel.objects.all()
    serializer_class = CategorySerializer

    def post(self, request, *args, **kwargs):
        serializer = CategorySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "success"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CategoryDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = CategoryModel.objects.all()
    serializer_class = CategorySerializer

    def get_object_or_404(self, queryset=None):
        try:
            return super().get_object()
        except Http404:
            raise Http404({"message": "Category not found"})

    def put(self, request, *args, **kwargs):
        instance = self.get_object_or_404()
        serializer = CategorySerializer(instance, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, *args, **kwargs):
        instance = self.get_object_or_404()
        serializer = CategorySerializer(instance, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, *args, **kwargs):
        instance = self.get_object_or_404()
        instance.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class GoodsView2(APIView):
    @swagger_auto_schema(
        tags=["View product list and details"], responses={200: "Success"}
    )
    def get(self, request, goods_id=None):
        """
        <View product>
        goods_id O -> View details
        goods_id
        * Separately removed due to merchant permission issues *
        """
        category_id = request.GET.get("category", "1")  # Default category ID
        category_name = request.GET.get("category_name")  # Category name if provided
        if category_name:
            category_id = get_object_or_404(CategoryModel, name=category_name).id

        if goods_id is None:
            category = request.GET.get(
                "category", "1"
            )  # You can provide default values.
            goods = GoodsModel.objects.all()
            if not goods.exists():
                return Response([], status=200)
            """
             <Filtering branch>
             - Latest
             - Old shoots
             - Price ascending & descending order
             - Ascending & descending number of reviews (5,6)
             """
            if category == "2":
                goods = goods.order_by("-price")
            elif category == "3":
                goods = goods.annotate(review_count=Count("reviewmodel")).order_by(
                    "-review_count"
                )
            elif category == "4":
                goods = goods.order_by("price")
            elif category == "5":
                goods = goods.annotate(order_count=Count("ordermodel")).order_by(
                    "-order_count"
                )
            elif category == "6":
                goods = goods.annotate(order_count=Count("ordermodel")).order_by(
                    "-created_at"
                )
            elif category == "7":
                goods = goods.filter(is_popular=True).order_by("-created_at")
            else:
                try:
                    goods = goods.order_by("-price")
                except Exception as e:
                    print(e)
                    return Response(
                        {"message": str(e)}, status=status.HTTP_400_BAD_REQUEST
                    )
            serializer = GoodsSerializer(goods, many=True)
            return Response(serializer.data, status=200)
            # return render(request, 'home.html', context={'data': serializer.data, "token": token})
        else:
            goods = get_object_or_404(GoodsModel, id=goods_id)
            serializer = GoodsDetailSerializer(goods)
            order_total = OrderModel.objects.filter(
                user_id=request.user.id, goods=goods
            ).count()
            review_total = ReviewModel.objects.filter(
                user_id=request.user.id, goods=goods
            ).count()
            result = serializer.data.copy()
            if order_total >= review_total:
                result["is_ordered"] = True
            else:
                result["is_ordered"] = False
            return Response(result, status=200)
            # return render(request, 'store/goods_detail.html', context={'goods': serializer.data})


# class GoodsView(APIView):
#     @swagger_auto_schema(
#         tags=["View product list and details"], responses={200: "Success"}
#     )
#     def get(self, request, goods_id=None):
#         category_name = request.GET.get("category_name")
#         category_type = request.GET.get("category_type", "1")  # Default category type
#         if goods_id is None:
#             if category_name:
#                 category = get_object_or_404(CategoryModel, name=category_name)
#                 goods = GoodsModel.objects.filter(category=category)
#             else:
#                 goods = GoodsModel.objects.all()

#             if not goods.exists():
#                 return Response([], status=200)
#             if category_type == "2":
#                 goods = goods.order_by("-price")
#             elif category_type == "3":
#                 goods = goods.annotate(review_count=Count("review")).order_by(
#                     "-review_count"
#                 )
#             elif category_type == "4":
#                 goods = goods.order_by("price")
#             elif category_type == "5":
#                 goods = goods.annotate(order_count=Count("ordermodel")).order_by(
#                     "-order_count"
#                 )
#             elif category_type == "6":
#                 goods = goods.annotate(order_count=Count("ordermodel")).order_by(
#                     "-created_at"
#                 )
#             elif category_type == "7":
#                 goods = goods.filter(is_popular=True).order_by("-created_at")
#             else:
#                 try:
#                     goods = goods.order_by("-price")
#                 except Exception as e:
#                     print(e)
#                     return Response(
#                         {"message": str(e)}, status=status.HTTP_400_BAD_REQUEST
#                     )

#             serializer = GoodsSerializer(goods, many=True)
#             return Response(serializer.data)
#         else:
#             goods = get_object_or_404(GoodsModel, id=goods_id)
#             serializer = GoodsDetailSerializer(goods)
#             order_total = OrderModel.objects.filter(
#                 user_id=request.user.id, goods=goods
#             ).count()
#             review_total = ReviewModel.objects.filter(
#                 user_id=request.user.id, goods=goods
#             ).count()
#             result = serializer.data.copy()
#             if order_total >= review_total:
#                 result["is_ordered"] = True
#             else:
#                 result["is_ordered"] = False
#             return Response(result, status=200)


class GoodsView(APIView):
    @swagger_auto_schema(
        tags=["View product list and details"], responses={200: "Success"}
    )
    def get(self, request, goods_id=None):
        category_name = request.GET.get("category_name")
        category_type = request.GET.get("category_type", "1")  # Default category type
        store_id = request.GET.get("store_id")

        if goods_id is None:
            goods = self.get_filtered_goods(category_name, category_type, store_id)

            if not goods.exists():
                return Response([], status=200)

            serializer = GoodsSerializer(goods, many=True)
            return Response(serializer.data)
        else:
            goods = get_object_or_404(GoodsModel, id=goods_id)
            serializer = GoodsDetailSerializer(goods)
            result = serializer.data.copy()
            result["is_ordered"] = self.is_ordered_by_user(request.user.id, goods)
            return Response(result, status=200)

    def get_filtered_goods(self, category_name, category_type, store_id):
        goods = GoodsModel.objects.all()

        if store_id:
            goods = goods.filter(store_id=store_id)

        if category_name:
            category = get_object_or_404(CategoryModel, name=category_name)
            goods = goods.filter(category=category)

        sorting_mapping = {
            "2": "-price",
            "3": "-review_count",
            "4": "price",
            "5": "-order_count",
            "1": "-created_at",
        }


        sorting_key = sorting_mapping.get(category_type, sorting_mapping["1"])

        if category_type == "3":
            goods = goods.annotate(review_count=Count("review"))

        if category_type in ["5", "6"]:
            goods = goods.annotate(order_count=Count("order"))

        if category_type == "7":
            goods = goods.filter(is_popular=True)

        try:
            goods = goods.order_by(sorting_key)
        except Exception as e:
            return Response({"message": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        return goods

    def is_ordered_by_user(self, user_id, goods):
        order_total = OrderModel.objects.filter(user_id=user_id, goods=goods).count()
        review_total = ReviewModel.objects.filter(user_id=user_id, goods=goods).count()
        return order_total >= review_total

# class GoodsView(generics.ListAPIView):
#     queryset = GoodsModel.objects.all()
#     serializer_class = GoodsSerializer
#     filter_backends = [filters.SearchFilter]
#     search_fields = ["name"]  # Specify fields you want to search
    
# class GoodsDetailView(generics.ListAPIView):
#     def get(self, request, goods_id):
#         goods = get_object_or_404(GoodsModel, id=goods_id)
#         serializer = GoodsDetailSerializer(goods)
#         result = serializer.data.copy()
#         result["is_ordered"] = self.is_ordered_by_user(request.user.id, goods)
#         return Response(result, status=200)
    
#     def is_ordered_by_user(self, user_id, goods):
#         order_total = OrderModel.objects.filter(user_id=user_id, goods=goods).count()
#         review_total = ReviewModel.objects.filter(user_id=user_id, goods=goods).count()
#         return order_total >= review_total

class StoreViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = StoreModel.objects.all()
    serializer_class = StoreSerializer


class StoreView(APIView):
    # permission_classes = [IsSeller]

    @swagger_auto_schema(
        tags=["Store information & product registration & store modification"],
        responses={200: "Success"},
    )
    def get(self, request, store_id):
        """
        <View store information>
        - Store basic information
        - List of products in the store
        """
        store = get_object_or_404(StoreModel, id=store_id)
        serializer = StoreSerializer(store)

        return Response(serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        tags=["Store information & product registration & store modification"],
        request_body=PostSerializer,
        responses={200: "Success"},
    )
    def post(self, request, store_id):
        """
        <Product Registration>
        Will be converted to multiple images
        """
        if request.data.get("goods_set"):
            for data in request.data.get("goods_set"):
                if data:
                    serializer = GoodsCreateSerializer(data=data)
                    category, is_created = CategoryModel.objects.get_or_create(
                        name=data.get("category")
                    )
                    if serializer.is_valid():
                        instance = serializer.save(category=category, store_id=store_id)
                        # Create sizes
                        sizes_data = data.get("sizes", [])
                        for size_data in sizes_data:
                            SizeModel.objects.create(product=instance, name=size_data)

                        # Create colors
                        colors_data = data.get("colors", [])
                        for color_data in colors_data:
                            ColorModel.objects.create(product=instance, name=color_data)

                        images_data = data.get("images", [])
                        if images_data:
                            for image_data in images_data:
                                format, imgstr = image_data.split(";base64,")
                                ext = format.split("/")[-1]
                                file_data = ContentFile(
                                    base64.b64decode(imgstr),
                                    name=f"{uuid.uuid4()}.{ext}",
                                )
                                ProductImage.objects.create(
                                    product=instance, image=file_data
                                )
                                # ImageModel.objects.create(goods=instance, image=file_data)
            return Response(
                {"message": "The product has been registered."},
                status=status.HTTP_201_CREATED,
            )
        return Response(
            {"message": "A problem has occurred."}, status=status.HTTP_400_BAD_REQUEST
        )

    @swagger_auto_schema(
        tags=["Store information & product registration & store modification"],
        request_body=PostSerializer,
        responses={200: "Success"},
    )
    def patch(self, request, store_id=None):
        store = get_object_or_404(StoreModel, id=store_id)
        data = {}
        try:
            for k, v in request.data.items():
                if v:
                    data[k] = v
        except Exception as e:
            return Response(
                {"message": "A problem has occurred."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if request.data.get("store_name"):
            return Response(
                {"message": "The store name cannot be changed."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = UpdateStoreSerializer(store, data=data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"message": "Store information has been modified."},
                status=status.HTTP_200_OK,
            )
        return Response(
            {"message": str(serializer.errors)}, status=status.HTTP_400_BAD_REQUEST
        )


class CreateProductAPIView(APIView):
    @swagger_auto_schema(
        tags=["Store information & product registration & store modification"],
        responses={200: "Success"},
    )
    def get(self, request, store_id):
        """
        <View store information>
        - Store basic information
        - List of products in the store
        """
        store = get_object_or_404(StoreModel, id=store_id)
        serializer = StoreSerializer(store)

        return Response(serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        tags=["Store information & product registration & store modification"],
        request_body=PostSerializer,
        responses={200: "Success"},
    )
    def post(self, request, store_id, format=None):
        products_data = request.data.get(
            "goods_set"
        )  # Get the list of products from request data
        created_products = []

        for product_data in products_data:
            product_data["store"] = store_id  # Assign store_id to each product data
            serializer = CreateProductSerializer(data=product_data)

            if serializer.is_valid():
                product = serializer.save()
                created_products.append(product)
            else:
                return Response(
                    {"message": "error", "errors": serializer.errors},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        return Response(
            {
                "message": "success",
                "products": [str(product) for product in created_products],
            },
            status=status.HTTP_201_CREATED,
        )


class CreateProductView(CreateAPIView):
    queryset = GoodsModel.objects.all()
    serializer_class = CreateProductSerializer

    def post(self, request, *args, **kwargs):
        data = request.data
        if isinstance(data, list):
            serializer = self.get_serializer(data=data, many=True)
        else:
            serializer = self.get_serializer(data=data)

        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# class UpdateProductAPIView(APIView):
#     def put(self, request, pk, format=None):
#         try:
#             product = GoodsModel.objects.get(pk=pk)
#         except GoodsModel.DoesNotExist:
#             return Response({"message": "Product not found"}, status=status.HTTP_404_NOT_FOUND)

#         serializer = UpdateProductSerializer(product, data=request.data)
#         if serializer.is_valid():
#             serializer.save()
#             return Response({"message": "success"}, status=status.HTTP_200_OK)
#         return Response({"message": "error"}, status=status.HTTP_400_BAD_REQUEST)


class UpdateProductAPIView(APIView):
    def get_object(self, pk):
        try:
            return GoodsModel.objects.get(pk=pk)
        except GoodsModel.DoesNotExist:
            raise status.HTTP_404_NOT_FOUND

    def put(self, request, pk, format=None):
        product = self.get_object(pk)
        serializer = UpdateProductSerializer(product, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "success"}, status=status.HTTP_200_OK)
        return Response(
            {"message": "error", "errors": serializer.errors},
            status=status.HTTP_400_BAD_REQUEST,
        )

    def patch(self, request, pk, format=None):
        product = self.get_object(pk)
        serializer = UpdateProductSerializer(product, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "success"}, status=status.HTTP_200_OK)
        return Response(
            {"message": "error", "errors": serializer.errors},
            status=status.HTTP_400_BAD_REQUEST,
        )


class DeleteProductAPIView(APIView):
    def delete(self, request, pk, format=None):
        try:
            product = GoodsModel.objects.get(pk=pk)
        except GoodsModel.DoesNotExist:
            return Response(
                {"message": "Product not found"}, status=status.HTTP_404_NOT_FOUND
            )

        # Delete related Size instances
        SizeModel.objects.filter(product=product).delete()

        # Delete related Color instances
        ColorModel.objects.filter(product=product).delete()

        # Delete related ProductImage instances
        ProductImage.objects.filter(product=product).delete()

        # Delete the Product instance
        product.delete()

        return Response({"message": "success"}, status=status.HTTP_200_OK)


class GoodsPatchView(APIView):
    # permission_classes = [IsSeller]

    @swagger_auto_schema(
        tags=["Multiple product modifications"],
        request_body=PostSerializer,
        responses={200: "Success"},
    )
    def patch(self, request):
        if request.data.get("goods_set"):
            for data in request.data.get("goods_set"):
                if data:
                    data = data.copy()
                    if "Kip" in data["price"]:
                        data["price"] = data["price"][:-1]
                    goods = get_object_or_404(GoodsModel, id=data.get("id"))
                    serializer = GoodsSerializer(goods, data=data, partial=True)
                    category, is_created = CategoryModel.objects.get_or_create(
                        name=data.get("category")
                    )
                    if serializer.is_valid():
                        instance = serializer.save(category=category)
                        images_data = data.get("images", [])
                        if images_data:
                            instance.imagemodel_set.all().delete()
                            for idx, image_data in enumerate(images_data):
                                # Convert Base64 encoded string to image file
                                # Delete all existing images and save as new -> It would be better to select the image and edit it later.
                                format, imgstr = image_data.split(";base64,")
                                ext = format.split("/")[-1]
                                file_data = ContentFile(
                                    base64.b64decode(imgstr),
                                    name=f"{uuid.uuid4()}.{ext}",
                                )
                                # Create a new image object and save it with the image file
                                ImageModel.objects.create(
                                    goods=instance, image=file_data
                                )
                    else:
                        print(serializer.errors)
            return Response(
                {"message": "The product has been modified."}, status=status.HTTP_200_OK
            )
        return Response(
            {"message": "A problem has occurred."}, status=status.HTTP_400_BAD_REQUEST
        )

    def delete(self, request):
        if request.data.get("goods_id"):
            goods = get_object_or_404(GoodsModel, id=request.data.get("goods_id"))
            goods.delete()
        return Response({"message": "success"}, status=status.HTTP_200_OK)


# Old review
class ReviewView(APIView):
    # permission_classes = [permissions.IsAuthenticated]
    """
    <Logic related to reviews>
    Edit and delete review -> pk = id of review
    """

    @swagger_auto_schema(
        tags=["View and write product reviews"], responses={200: "Success"}
    )
    def get(self, request, pk):
        # pk = product id
        review = ReviewModel.objects.filter(goods_id=pk).order_by("-created_at")
        serializer = ReviewSerializer(review, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        tags=["View and write product reviews"],
        request_body=PostSerializer,
        responses={201: "Created"},
    )
    def post(self, request, pk):
        # pk = product id
        review = ReviewModel.objects.filter(user=request.user, goods_id=pk).exists()
        order = OrderModel.objects.filter(user=request.user, goods_id=pk).exists()
        if not order:
            return Response(
                {"message": "Only users who have placed an order can leave a review."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if review:
            return Response(
                {"message": "I've already written a review."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        serializer = ReviewSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save(goods_id=pk, user=request.user)
            return Response(
                {"message": "Review completed"}, status=status.HTTP_201_CREATED
            )
        return Response(
            {"message": "Please use after logging in."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    def patch(self, request, pk):
        review = get_object_or_404(ReviewModel, id=pk, user=request.user)
        serializer = ReviewSerializer(review, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "success"}, status=status.HTTP_200_OK)
        return Response(
            {"message": serializer.errors}, status=status.HTTP_400_BAD_REQUEST
        )

    def delete(self, request, pk):
        review = get_object_or_404(ReviewModel, id=pk, user=request.user)
        review.delete()
        return Response({"message": "success"}, status=status.HTTP_200_OK)


# new review
class ReviewList(generics.ListCreateAPIView):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer


class ReviewCreate(generics.ListCreateAPIView):
    queryset = Review.objects.all()
    serializer_class = ReviewCreateSerializer


class ReviewRetrieveUpdateDestroy(generics.RetrieveUpdateDestroyAPIView):
    queryset = Review.objects.all()
    serializer_class = ReviewCreateSerializer
    permission_classes = [IsOwnerOrReadOnly]


class UserReviewListView(generics.ListAPIView):
    serializer_class = ReviewSerializer

    def get_queryset(self):
        user_id = self.kwargs["user_id"]
        return Review.objects.filter(user_id=user_id)


class ProductReviewListView(generics.ListAPIView):
    serializer_class = ReviewSerializer

    def get_queryset(self):
        product_id = self.kwargs["product_id"]
        return Review.objects.filter(product_id=product_id)


# class ReviewDeleteView(generics.DestroyAPIView):
#     def delete(self, request, pk, format=None):
#         try:
#             review = Review.objects.get(pk=pk)
#         except Review.DoesNotExist:
#             return Response({"message": "Review not found"}, status=status.HTTP_404_NOT_FOUND)

#         review.delete()

#         return Response({"message": "success"}, status=status.HTTP_204_NO_CONTENT)


class ReviewByProductAndUserAPIView(generics.RetrieveAPIView):
    serializer_class = ReviewSerializer

    def get_object(self):
        product_id = self.kwargs["product_id"]
        user_id = self.kwargs["user_id"]

        try:
            review = Review.objects.get(product_id=product_id, user_id=user_id)
            return review
        except Review.DoesNotExist:
            return None

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()

        if instance is None:
            content = {"detail": "Review not found."}
            return Response(content, status=status.HTTP_404_NOT_FOUND)

        serializer = self.get_serializer(instance)
        return Response(serializer.data)


class CheckReview(APIView):
    def post(self, request, pk):
        review = ReviewModel.objects.filter(user=request.user, goods_id=pk).exists()
        order = OrderModel.objects.filter(user=request.user, goods_id=pk).exists()
        if not order:
            return Response(
                {"message": "Only users who have placed an order can leave a review."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if review:
            return Response(
                {"message": "I've already written a review."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        return Response({"message": "success"}, status=status.HTTP_200_OK)


class TermsAPI(APIView):
    def get(self, request, pk):
        # 1: Terms of Use, 2: Privacy Policy
        turm = PolicyModel.objects.filter(category=pk).last()
        content = turm.content if turm else ""
        return Response({"content": content}, status=status.HTTP_200_OK)


def review_form(request, pk):
    form = ReviewForm()
    return render(request, "store/review.html", {"form": form, "goods_id": pk})


def review_list(request, pk):
    return render(request, "store/review_list.html", {"goods_id": pk})


# Old one
class OrderView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    """
    <Product order logic>
    """

    @swagger_auto_schema(
        tags=["Product ordering and inquiry"], responses={200: "Success"}
    )
    def get(self, request):
        order_set = (
            OrderModel.objects.filter(user=request.user).distinct().values("goods")
        )
        data = []
        if order_set:
            for order in order_set:
                goods = GoodsModel.objects.get(id=order["goods"])
                data.append(GoodsSerializer(goods).data)
            return Response(data, status=status.HTTP_200_OK)
        return Response([], status=status.HTTP_200_OK)

    @swagger_auto_schema(
        tags=["Product ordering and inquiry"],
        request_body=PostSerializer,
        responses={200: "Success"},
    )
    def post(self, request):
        goods_id = request.data.get("goods_id")

        goods = get_object_or_404(GoodsModel, id=goods_id)
        goods = GoodsSerializer(goods).data.copy()

        serializer = OrderSerializer(data=goods)

        if serializer.is_valid(raise_exception=True):
            try:
                serializer.save(user=request.user, goods_id=goods_id)
                return Response(
                    {"message": "I ordered a product."}, status=status.HTTP_200_OK
                )
            except Exception as e:
                return Response({"message": str(e)}, status=status.HTTP_400_BAD_REQUEST)


# New one
# Order
class OrderListView(generics.ListCreateAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer

    def get_queryset(self):
        # Retrieve orders with status "Pending"
        return Order.objects.filter(status="Pending")


class OrderDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer


class UserOrderListView(generics.ListAPIView):
    serializer_class = OrderSerializer

    def get_queryset(self):
        user_id = self.kwargs["user_id"]
        return Order.objects.filter(user_id=user_id)


# class CreateOrderView(generics.CreateAPIView):
#     queryset = Order.objects.all()
#     serializer_class = OrderSerializer


# class OrderCreateAPIView(APIView):
#     def post(self, request):
#         serializer = OrderCreateSerializer(data=request.data)
#         if serializer.is_valid():
#             serializer.save()
#             return Response({"message": "success"}, status=status.HTTP_201_CREATED)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
# class OrderCreateAPIView(APIView):
#     def post(self, request):
#         serializer = OrderCreateSerializer(data=request.data)
#         if serializer.is_valid():
#             serializer.save()
#             return Response({"message": "success"}, status=status.HTTP_201_CREATED)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class OrderCreateAPIView(APIView):
    def post(self, request):
        # Check if the user is authenticated
        if request.user and request.user.is_authenticated:
            request.data._mutable = True
            request.data['user'] = request.user.id  # Set the user field to the authenticated user
            request.data._mutable = False
        
        serializer = OrderCreateSerializer(data=request.data)
        print(serializer)
        if serializer.is_valid():
            try:
                serializer.save()
                return Response({"message": "Order created successfully"}, status=status.HTTP_201_CREATED)
            except Exception as e:
                return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

class OrderUpdateAPIView(APIView):
    def put(self, request, pk):
        try:
            order = Order.objects.get(pk=pk)
        except Order.DoesNotExist:
            return Response(
                {"error": "Order not found"}, status=status.HTTP_404_NOT_FOUND
            )

        serializer = OrderUpdateSerializer(order, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class OrderUpdateChinaUrlAPIView(APIView):
    def put(self, request, pk):
        try:
            order = Order.objects.get(pk=pk)
        except Order.DoesNotExist:
            return Response(
                {"error": "Order not found"}, status=status.HTTP_404_NOT_FOUND
            )

        serializer = OrderUpdateChinaUrlSerializer(order, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class OrderUpdateLaoUrlAPIView(APIView):
    def put(self, request, pk):
        try:
            order = Order.objects.get(pk=pk)
        except Order.DoesNotExist:
            return Response(
                {"error": "Order not found"}, status=status.HTTP_404_NOT_FOUND
            )

        serializer = OrderUpdateLaoUrlSerializer(order, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class OrderUpdateBillAPIView(APIView):
    def put(self, request, pk):
        try:
            order = Order.objects.get(pk=pk)
        except Order.DoesNotExist:
            return Response(
                {"error": "Order not found"}, status=status.HTTP_404_NOT_FOUND
            )

        serializer = OrderUpdateBillSerializer(order, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class OrderDeleteView(generics.DestroyAPIView):
    def delete(self, request, pk, format=None):
        try:
            order = Order.objects.get(pk=pk)
        except Order.DoesNotExist:
            return Response(
                {"message": "Order not found"}, status=status.HTTP_404_NOT_FOUND
            )

        # Delete related OrderItem instances
        OrderItem.objects.filter(order_id=order).delete()

        # Delete the Order instance
        order.delete()

        return Response({"message": "success"}, status=status.HTTP_204_NO_CONTENT)


# class PendingOrderListAPIView(generics.ListAPIView):
#     queryset = Order.objects.filter(status='Pending')
#     serializer_class = PendingOrderSerializer

# class ProcessingOrderListAPIView(generics.ListAPIView):
#     queryset = Order.objects.filter(status='Processing')
#     serializer_class = ProcessingOrderSerializer

# class ShippedOrderListAPIView(generics.ListAPIView):
#     queryset = Order.objects.filter(status='Shipped')
#     serializer_class = ShippedOrderSerializer

# class DeliveredOrderListAPIView(generics.ListAPIView):
#     queryset = Order.objects.filter(status='Delivered')
#     serializer_class = DeliveredOrderSerializer

# class DeliveredOrderListAPIView(generics.ListAPIView):
#     serializer_class = DeliveredOrderSerializer

#     def get_queryset(self):
#         return Order.objects.filter(status='Delivered')


class PendingOrderListAPIView(generics.ListAPIView):
    serializer_class = PendingOrderSerializer

    def get_queryset(self):
        store_id = self.request.query_params.get("store_id", None)
        queryset = Order.objects.filter(status="Pending")
        if store_id:
            queryset = queryset.filter(store_id=store_id)
        return queryset

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.serializer_class(queryset, many=True)
        return response.Response(
            {"count": len(serializer.data), "orders": serializer.data}
        )

class PendingOrderListAPIView3(generics.ListAPIView):
    serializer_class = PendingOrderSerializer
    # pagination_class = OrderPagination  # Optional: Add pagination

    def get_queryset(self):
        store_id = self.request.query_params.get("store_id", None)
        queryset = Order.objects.filter(status="Pending")
        if store_id:
            queryset = queryset.filter(store_id=store_id)
        return queryset

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_paginated_response(self.serializer_class(page, many=True).data)
        else:
            serializer = self.serializer_class(queryset, many=True)
        return response.Response({"count": len(serializer.data), "orders": serializer.data})

class PendingOrderListAPIView4(generics.ListAPIView):
    serializer_class = PendingOrderSerializer
    # pagination_class = OrderPagination  # Optional: Add pagination

    def get_queryset(self):
        queryset = Order.objects.filter(status="Pending")
        
        # Optional filters
        store_id = self.request.query_params.get("store_id", None)
        tel = self.request.query_params.get("tel", None)
        province = self.request.query_params.get("province", None)
        district = self.request.query_params.get("district", None)
        shipping_company = self.request.query_params.get("shipping_company", None)
        date_filter = self.request.query_params.get("date_filter", None)
        
        # Apply filters if provided in query parameters
        if store_id:
            queryset = queryset.filter(store_id=store_id)
        if tel:
            queryset = queryset.filter(tel__icontains=tel)
        if province:
            queryset = queryset.filter(province__icontains=province)
        if district:
            queryset = queryset.filter(district__icontains=district)
        if shipping_company:
            queryset = queryset.filter(shipping_company__icontains=shipping_company)
        
        # Apply date-based filters
        if date_filter:
            today = timezone.now().date()
            if date_filter == "month":
                start_date = today.replace(day=1)
                queryset = queryset.filter(created_at__date__gte=start_date)
            elif date_filter == "q1":
                start_date = today.replace(month=1, day=1)
                end_date = today.replace(month=3, day=31)
                queryset = queryset.filter(created_at__date__gte=start_date, created_at__date__lte=end_date)
            elif date_filter == "q2":
                start_date = today.replace(month=4, day=1)
                end_date = today.replace(month=6, day=30)
                queryset = queryset.filter(created_at__date__gte=start_date, created_at__date__lte=end_date)
            elif date_filter == "q3":
                start_date = today.replace(month=7, day=1)
                end_date = today.replace(month=9, day=30)
                queryset = queryset.filter(created_at__date__gte=start_date, created_at__date__lte=end_date)
            elif date_filter == "q4":
                start_date = today.replace(month=10, day=1)
                end_date = today.replace(month=12, day=31)
                queryset = queryset.filter(created_at__date__gte=start_date, created_at__date__lte=end_date)
            elif date_filter == "year":
                start_date = today.replace(month=1, day=1)
                queryset = queryset.filter(created_at__date__gte=start_date)

        return queryset

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_paginated_response(self.serializer_class(page, many=True).data)
        else:
            serializer = self.serializer_class(queryset, many=True)
        return response.Response({"count": len(serializer.data), "orders": serializer.data})


class DeliveredOrderListAPIView(generics.ListAPIView):
    serializer_class = DeliveredOrderSerializer

    def get_queryset(self):
        queryset = Order.objects.filter(status="Delivered")
        
        date_filter = self.request.query_params.get("date_filter", None)
        
        
        # Apply date-based filters
        if date_filter:
            today = timezone.now().date()
            if date_filter == "month":
                start_date = today.replace(day=1)
                queryset = queryset.filter(created_at__date__gte=start_date)
            elif date_filter == "q1":
                start_date = today.replace(month=1, day=1)
                end_date = today.replace(month=3, day=31)
                queryset = queryset.filter(created_at__date__gte=start_date, created_at__date__lte=end_date)
            elif date_filter == "q2":
                start_date = today.replace(month=4, day=1)
                end_date = today.replace(month=6, day=30)
                queryset = queryset.filter(created_at__date__gte=start_date, created_at__date__lte=end_date)
            elif date_filter == "q3":
                start_date = today.replace(month=7, day=1)
                end_date = today.replace(month=9, day=30)
                queryset = queryset.filter(created_at__date__gte=start_date, created_at__date__lte=end_date)
            elif date_filter == "q4":
                start_date = today.replace(month=10, day=1)
                end_date = today.replace(month=12, day=31)
                queryset = queryset.filter(created_at__date__gte=start_date, created_at__date__lte=end_date)
            elif date_filter == "year":
                start_date = today.replace(month=1, day=1)
                queryset = queryset.filter(created_at__date__gte=start_date)

        return queryset

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        
        # Check if the download parameter is present
        if request.query_params.get("download") == "true":
            return self.download_excel(queryset)
        
        # Standard API response
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_paginated_response(self.serializer_class(page, many=True).data)
        else:
            serializer = self.serializer_class(queryset, many=True)
        return response.Response({"count": len(serializer.data), "orders": serializer.data})

    def download_excel(self, queryset):
        # Create a workbook and sheet
        wb = Workbook()
        ws = wb.active
        ws.title = "Deliveried Orders"

        # Write the header for orders
        order_headers = [
            'Order ID', 'User Email', 'Store', 'Telephone', 'Total Prices', 
            'Address', 'Created At', 'Status', 'Product', 'Quantity', 
            'Price', 'Is_seted'
        ]
        ws.append(order_headers)

        # Write data rows for orders and items
        for order in queryset:
            order_base_row = [
                order.id,
                order.user.email if order.user else 'Guest',
                order.store.name if order.store else 'aa',
                order.tel,
                order.total_prices,
                order.district,
                order.created_at.strftime("%Y-%m-%d %H:%M:%S"),
                order.status,
            ]
            # Add each item related to the order
            for item in order.orderitem_set.all():
                row = order_base_row + [
                    item.product.name if item.product else '',
                    item.quantity,
                    item.price,
                    item.color,
                ]
                ws.append(row)

        # Prepare the response
        response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = 'attachment; filename="deliveried_orders.xlsx"'
        
        # Save the workbook to the response
        wb.save(response)

        return response
    
    
class ProcessingOrderListAPIView(generics.ListAPIView):
    serializer_class = ProcessingOrderSerializer

    def get_queryset(self):
        store_id = self.request.query_params.get("store_id", None)
        queryset = Order.objects.filter(status="Processing")
        if store_id:
            queryset = queryset.filter(store_id=store_id)
        return queryset

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.serializer_class(queryset, many=True)
        return response.Response(
            {"count": len(serializer.data), "orders": serializer.data}
        )


class ShippedOrderListAPIView(generics.ListAPIView):
    serializer_class = ShippedOrderSerializer

    def get_queryset(self):
        store_id = self.request.query_params.get("store_id", None)
        queryset = Order.objects.filter(status="Shipped")
        if store_id:
            queryset = queryset.filter(store_id=store_id)
        return queryset

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.serializer_class(queryset, many=True)
        return response.Response(
            {"count": len(serializer.data), "orders": serializer.data}
        )


class DeliveredOrderListAPIView2(generics.ListAPIView):
    serializer_class = DeliveredOrderSerializer

    def get_queryset(self):
        store_id = self.request.query_params.get("store_id", None)
        queryset = Order.objects.filter(status="Delivered")
        if store_id:
            queryset = queryset.filter(store_id=store_id)
        return queryset

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.serializer_class(queryset, many=True)
        return response.Response(
            {"count": len(serializer.data), "orders": serializer.data}
        )


# class PendingOrderListAPIView(generics.ListAPIView):
#     serializer_class = PendingOrderSerializer

#     def get_queryset(self):
#         return Order.objects.filter(status='Pending')

#     def get(self, request, *args, **kwargs):
#         queryset = self.get_queryset()
#         count = queryset.count()
#         serializer = self.serializer_class(queryset, many=True)
#         return Response({
#             'count': count,
#             'orders': serializer.data
#         })


# class ProcessingOrderListAPIView(generics.ListAPIView):
#     serializer_class = ProcessingOrderSerializer

#     def get_queryset(self):
#         return Order.objects.filter(status="Processing")

#     def get(self, request, *args, **kwargs):
#         queryset = self.get_queryset()
#         count = queryset.count()
#         serializer = self.serializer_class(queryset, many=True)
#         return Response({"count": count, "orders": serializer.data})


# class ShippedOrderListAPIView(generics.ListAPIView):
#     serializer_class = ShippedOrderSerializer

#     def get_queryset(self):
#         return Order.objects.filter(status="Shipped")

#     def get(self, request, *args, **kwargs):
#         queryset = self.get_queryset()
#         count = queryset.count()
#         serializer = self.serializer_class(queryset, many=True)
#         return Response({"count": count, "orders": serializer.data})


# class DeliveredOrderListAPIView(generics.ListAPIView):
#     serializer_class = DeliveredOrderSerializer

#     def get_queryset(self):
#         return Order.objects.filter(status="Delivered")

#     def get(self, request, *args, **kwargs):
#         queryset = self.get_queryset()
#         count = queryset.count()
#         serializer = self.serializer_class(queryset, many=True)
#         return Response({"count": count, "orders": serializer.data})


class SearchView(APIView):
    @swagger_auto_schema(
        tags=["search"], request_body=PostSerializer, responses={200: "Success"}
    )
    def post(self, request):
        search_word = request.data.get("search")
        goods_set = GoodsModel.objects.filter(
            Q(name__icontains=search_word) | Q(store__name__icontains=search_word)
        )

        goods = GoodsSerializer(goods_set, many=True).data

        return Response(goods, status=status.HTTP_200_OK)


def resize_image(image_data, output_size=(800, 600), quality=85):
    """
    Adjust the resolution of the image file and save it in JPEG format.
    :param image_data: Original image data (base64 encoded string).
    :param output_size: Size (width, height) of the image to be changed.
    :param quality: JPEG storage quality (1-100).
    :return: Changed image data (base64 encoded string).
    """
    # Convert image data to PIL image object
    image = Image.open(io.BytesIO(base64.b64decode(image_data)))

    # Change image size
    image = image.resize(output_size, Image.ANTIALIAS)

    # Save in JPEG format
    output_buffer = io.BytesIO()
    image.save(output_buffer, format="JPEG", quality=quality)
    output_data = base64.b64encode(output_buffer.getvalue()).decode()

    return output_data


# Bank account
class BankAccountListCreateAPIView(generics.ListCreateAPIView):
    queryset = BankAccount.objects.all()
    serializer_class = BankAccountSerializer


class BankAccountRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = BankAccount.objects.all()
    serializer_class = BankAccountSerializer


def check_store_bank_account(request, store_id):
    try:
        store = StoreModel.objects.get(pk=store_id)
    except StoreModel.DoesNotExist:
        return JsonResponse({"error": "Store not found"}, status=404)

    # Check if the store has a bank account
    has_bank_account = BankAccount.objects.filter(store=store).exists()

    return JsonResponse({"has_bank_account": has_bank_account})


class BankAccountViewSet(viewsets.ModelViewSet):
    queryset = BankAccount.objects.all()
    serializer_class = BankAccountSerializer2

    def list(self, request, *args, **kwargs):
        store_id = self.request.query_params.get("store_id")
        if store_id:
            queryset = self.queryset.filter(store_id=store_id)
        else:
            queryset = self.queryset.none()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class BankAccountUpdateAPIView(generics.UpdateAPIView):
    queryset = BankAccount.objects.all()
    serializer_class = BankAccountSerializer

    def update(self, request, *args, **kwargs):
        store_id = kwargs.get("store_id")
        try:
            # Retrieve the bank account associated with the given store ID
            bank_account = BankAccount.objects.get(store_id=store_id)
        except BankAccount.DoesNotExist:
            # If bank account does not exist, return a not found response
            return Response(
                {"message": "Bank account not found for the given store ID"},
                status=status.HTTP_404_NOT_FOUND,
            )

        # Serialize the bank account with the updated data
        serializer = self.get_serializer(bank_account, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=status.HTTP_200_OK)


# Website infomation
# class WebInfoListCreateAPIView(generics.ListCreateAPIView):
#     queryset = WebInfo.objects.all()
#     serializer_class = WebInfoSerializer


# class WebInfoRetrieveUpdateAPIView(generics.RetrieveUpdateAPIView):
#     queryset = WebInfo.objects.all()
#     serializer_class = WebInfoSerializer
#     lookup_field = "pk"  # Use 'pk' as the lookup field for retrieving and updating the WebInfo object

class WebInfoList(generics.ListAPIView):
    queryset = WebInfo.objects.all()
    serializer_class = WebInfoSerializer

# class WebInfoRetrieveUpdateDestroy(generics.RetrieveUpdateDestroyAPIView):
#     queryset = WebInfo.objects.all()
#     serializer_class = WebInfoSerializer

class WebInfoCreateOrUpdate(APIView):

    def patch(self, request, *args, **kwargs):
        try:
            # Assuming there's only one instance of WebInfo to update
            webinfo = WebInfo.objects.first()
            if webinfo:
                serializer = WebInfoSerializer(webinfo, data=request.data)
            else:
                serializer = WebInfoSerializer(data=request.data)

            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"detail": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        
# Hotel QR management
class HotelQRListCreateAPIView(generics.ListCreateAPIView):
    queryset = HotelQR.objects.all()
    serializer_class = HotelQRSerializers


class HotelQRRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = HotelQR.objects.all()
    serializer_class = HotelQRSerializers
    