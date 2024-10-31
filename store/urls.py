from django.conf.urls.static import static
from django.urls import path, include
from django.conf import settings
from store import views
from rest_framework.routers import DefaultRouter
from .views import BankAccountViewSet

router = DefaultRouter()
router.register(r'bank-accounts/detail', BankAccountViewSet)


urlpatterns = [
    path("categories", views.CategoryListCreate.as_view(), name='category-list-create'),
    path("categories/<int:pk>", views.CategoryDetail.as_view(), name='category-detail'),
    path("all-stores", views.StoreViewSet.as_view({'get': 'list'}), name='store-list'),
    path("", views.GoodsView.as_view(), name="goods_list"),  # Product list related
    path("detail/<int:goods_id>", views.GoodsView.as_view(), name="goods_detail"),  # Product list related
    # path("<int:store_id>", views.CreateProductAPIView.as_view(), name="store"),  # Store Related Related
    path("<int:store_id>", views.StoreView.as_view(), name="store"),  # Store Related Related
    path('product/create', views.CreateProductAPIView.as_view(), name='create-product'),
    path('product/create2', views.CreateProductView.as_view(), name='create-product'),
    path('product/update/<int:pk>', views.UpdateProductAPIView.as_view(), name='update-product'),
    path('product/delete/<int:pk>', views.DeleteProductAPIView.as_view(), name='delete-product'),
    path(
        "goods", views.GoodsPatchView.as_view(), name="goods_change"
    ),  # Related to modifying goods -> Placement of different views due to permission settings
    path(
        "goods/<int:goods_id>", views.GoodsView.as_view(), name="goods_detail"
    ),  # Product related
    path("review/<int:pk>", views.ReviewView.as_view(), name="review"),  # Review related
    
    # old order
    path("order", views.OrderView.as_view(), name="order"),  # Order related
    # new order
    path('orders', views.OrderListView.as_view(), name='order-list'),
    path('order/create', views.OrderCreateAPIView.as_view(), name='order-create'),
    path('order/update/<int:pk>', views.OrderUpdateAPIView.as_view(), name='order-update'),
    path('order/update/china-url/<int:pk>', views.OrderUpdateChinaUrlAPIView.as_view(), name='order-update-china-url'),
    path('order/update/lao-url/<int:pk>', views.OrderUpdateLaoUrlAPIView.as_view(), name='order-update-lao-url'),
    path('order/update/order-bill/<int:pk>', views.OrderUpdateBillAPIView.as_view(), name='order-update-bill'),
    path('order/<int:pk>', views.OrderDetailView.as_view(), name='order-detail'),
    path('user/<int:user_id>/order', views.UserOrderListView.as_view(), name='user-order-list'),
    path('order/delete/<int:pk>', views.OrderDeleteView.as_view(), name='delete-order'),
    path('order/pending/', views.PendingOrderListAPIView.as_view(), name='pending-orders'),
    path('order/processing/', views.ProcessingOrderListAPIView.as_view(), name='processing-orders'),
    path('order/shipped/', views.ShippedOrderListAPIView.as_view(), name='shipped-orders'),
    path('order/delivered/', views.DeliveredOrderListAPIView.as_view(), name='delivered-orders'),
    path("search", views.SearchView.as_view(), name="search"),  # Order related
    path("check-review/<int:pk>", views.CheckReview.as_view(), name="CheckReview"),  # Order related
    path("terms/<int:pk>", views.TermsAPI.as_view(), name="terms"),  # Order related
    # Template render only
    path("review/form/<int:pk>", views.review_form, name="review_form"),
    path("review/list/<int:pk>", views.review_list, name="review_list"),
    # # Review
    path('reviews', views.ReviewList.as_view(), name='review-list'),
    path('review/create', views.ReviewCreate.as_view(), name='review-create'),
    path('review/<int:pk>', views.ReviewRetrieveUpdateDestroy.as_view(), name='review-detail'),
    path('reviews/by-product/<int:product_id>/user/<int:user_id>', views.ReviewByProductAndUserAPIView.as_view(), name='review-by-product-and-user'),
    # path('review/update/<int:pk>', views.ReviewRetrieveUpdateDestroy.as_view(), name='review-update'),
    # path('user/<int:user_id>/review', views.UserReviewListView.as_view(), name='user-reviews-list'),
    path('product/<int:product_id>/review', views.ProductReviewListView.as_view(), name='product-reviews-list'),
    # path('review/delete/<int:pk>', views.ReviewDeleteView.as_view(), name='delete-reviews'),

    path("goods/list", views.goods_list, name="goods_list"),
    path("goods/detail/<int:goods_id>", views.goods_detail, name="goods_detail"),
    path("order/list", views.order_list, name="order_list"),
    path("setting", views.store_setting, name="store_setting"),
    # bank account
    path('bank-accounts', views.BankAccountListCreateAPIView.as_view(), name='bank-account-list-create'),
    path('bank-accounts/<int:pk>', views.BankAccountRetrieveUpdateDestroyAPIView.as_view(), name='bank-account-detail'),
    path('bank-accounts/<int:store_id>/has_bank_account', views.check_store_bank_account, name='check_store_bank_account'),
    path('', include(router.urls)),
    path('bank-accounts/update/<int:store_id>', views.BankAccountUpdateAPIView.as_view(), name='bank-account-update'),
    # Web info
    path("web-info", views.WebInfoList.as_view(), name="web-info-list"),
    path("web-info/create_update", views.WebInfoCreateOrUpdate.as_view(), name="edit-update-web-information"),
    # Notice
    path("notice", views.NoticeList.as_view(), name="list-notice"),
    path("notice/create", views.NoticeCreate.as_view(), name="list-notice"),
    path("notice/detail/<int:pk>", views.NoticeDetailDelete.as_view(), name="detail-notice"),
    path("notice/delete/<int:pk>", views.NoticeDetailDelete.as_view(), name="delete-notice"),
    path("notice/update/<int:pk>", views.NoticeUpdate.as_view(), name="update-notice"),
    # hotel QR
    path('hotel-qr', views.HotelQRListCreateAPIView.as_view(), name='hotel-qr-list-create'),
    path('hotel-qr/<int:pk>', views.HotelQRRetrieveUpdateDestroyAPIView.as_view(), name='hotel-qr-detail'),
]
# urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
