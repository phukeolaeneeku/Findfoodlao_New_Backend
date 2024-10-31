from django.contrib import admin

from .models import (
    StoreModel,
    OrderModel,
    ReviewModel,
    CategoryModel,
    ImageModel,
    GoodsModel,
    FilteringModel,
    PolicyModel,
    Order,
    OrderItem,
    ProductImage,
    BankAccount,
    Review,
    SizeModel,
    ColorModel,
    WebInfo,
    NoticeModel,
    HotelQR
)


@admin.register(StoreModel)
class StoreAdmin(admin.ModelAdmin):
    """Board Admin Definition"""

    list_display = (
        "name",
        "seller",
        "address",
    )

    search_fields = (
        "name",
        "seller",
    )


@admin.register(CategoryModel)
class CategoryAdmin(admin.ModelAdmin):
    """Board Admin Definition"""

    list_display = ("name",)

    search_fields = ("name",)


@admin.register(GoodsModel)
class GoodsAdmin(admin.ModelAdmin):
    """Board Admin Definition"""

    list_display = (
        "category",
        "store",
        "name",
        "price",
    )

    search_fields = ("name", "store")

    list_filter = ("category",)


@admin.register(OrderModel)
class OrderAdmin(admin.ModelAdmin):
    """Board Admin Definition"""

    list_display = ("goods", "price", "user", "ordered_at")

    search_fields = ("user", "goods")


@admin.register(ReviewModel)
class ReviewModelAdmin(admin.ModelAdmin):
    list_display = ("goods", "user", "star")

    search_fields = ("user", "goods")

    list_filter = ("star",)


@admin.register(ImageModel)
class ImageModelAdmin(admin.ModelAdmin):
    """Board Admin Definition"""

    list_display = ("goods", "image")

    search_fields = ("goods",)


@admin.register(FilteringModel)
class FilteringModelAdmin(admin.ModelAdmin):
    """Board Admin Definition"""

    list_display = ("id", "filter", "option")
    list_display_links = ("filter", "option")

    search_fields = ("filtering",)


@admin.register(PolicyModel)
class FilteringModelAdmin(admin.ModelAdmin):
    """Board Admin Definition"""

    list_display = ("id", "category")
    list_display_links = ("category",)

    search_fields = ("category",)

admin.site.register(Order)
admin.site.register(OrderItem)
admin.site.register(ProductImage)
admin.site.register(BankAccount)
admin.site.register(Review)
admin.site.register(SizeModel)
admin.site.register(ColorModel)
admin.site.register(WebInfo) 
admin.site.register(NoticeModel)
admin.site.register(HotelQR)
