from django.urls import include, path
from rest_framework_nested import routers
from restaurant2 import views
router = routers.DefaultRouter()
router.register(r'', views.RestaurantCreateView, basename='restaurants')

urlpatterns = [
    # Restaurant
    path('', views.RestaurantCreateView.as_view(), name='restaurant-list-create'),
    path('<int:pk>/', views.RestaurantDetailView.as_view(), name='restaurant-detail'),
    # Category
    path('<int:restaurant_pk>/categories/list/', views.CategoryListView.as_view(), name='category-list'),
    path('<int:restaurant_pk>/categories/create/', views.CategoryCreateView.as_view(), name='category-list-create'),
    path('<int:restaurant_pk>/categories/<int:pk>/update/', views.CategoryUpdateView.as_view(), name='category-update'),
    path('<int:restaurant_pk>/categories/<int:pk>/detail/', views.CategoryDetailView.as_view(), name='category-detail'),
    path('<int:restaurant_pk>/categories/<int:pk>/delete/', views.CategoryDestroyView.as_view(), name='category-delete'),
    # employee
    path('<int:restaurant_pk>/employees/list/', views.EmployeeListView.as_view(), name='employee-list'),
    # path('<int:restaurant_pk>/employees/create/', views.EmployeeCreateView.as_view(), name='employee-create'),
    path('<int:restaurant_pk>/employees/<int:pk>/update/', views.EmployeeUpdateView.as_view(), name='employee-update'),
    path('<int:restaurant_pk>/employees/<int:pk>/detail/', views.EmployeeDetailView.as_view(), name='employee-dertail'),
    path('<int:restaurant_pk>/employees/<int:pk>/delete/', views.EmployeeDestroyView.as_view(), name='employee-delete'),
    # table
    path('<int:restaurant_pk>/tables/list/', views.TableListView.as_view(), name='table-list'),
    path('<int:restaurant_pk>/tables/create/', views.TableCreateView.as_view(), name='table-create'),
    path('<int:restaurant_pk>/tables/<int:pk>/update/', views.TableUpdateView.as_view(), name='table-update'),
    path('<int:restaurant_pk>/tables/<int:pk>/detail/', views.TableDetailView.as_view(), name='table-detail'),
    path('<int:restaurant_pk>/tables/<int:pk>/delete/', views.TableDestroyView.as_view(), name='table-delete'),
    # point
    path('<int:restaurant_pk>/points/', views.PointListCreateView.as_view(), name='point-list-create'),
    path('<int:restaurant_pk>/points/<int:pk>/', views.PointDetailView.as_view(), name='point-detail'),
    # Menu items 
    path('<int:restaurant_pk>/menu_items/list/', views.MenuItemListView.as_view(), name='menuitem-list'),
    path('<int:restaurant_pk>/menu_items/create/', views.MenuItemCreateView.as_view(), name='menuitem-create'),
    path('<int:restaurant_pk>/menu_items/<int:pk>/update/', views.MenuItemUpdateView.as_view(), name='menuitem-update'),
    path('<int:restaurant_pk>/menu_items/<int:pk>/detail/', views.MenuItemDetailView.as_view(), name='menuitem-detail'),
    path('<int:restaurant_pk>/menu_items/<int:pk>/delete/', views.MenuItemDestroyView.as_view(), name='menuitem-delete'),
    # Order management
    # path('<int:restaurant_pk>/orders/list/', views.OrderListView.as_view(), name='order-list'),
    # path('<int:restaurant_pk>/orders/create/', views.OrderCreateView.as_view(), name='order-create'),
    # path('<int:restaurant_pk>/orders/<int:pk>/update/', views.OrderUpdateView.as_view(), name='order-update'),
    # path('<int:restaurant_pk>/orders/<int:pk>/detail/', views.OrderDetailView.as_view(), name='order-detail'),
    # path('<int:restaurant_pk>/orders/<int:pk>/delete/', views.OrderDestroyView.as_view(), name='order-delete'),
    # path('<int:restaurant_pk>/orders/<int:pk>/cancel/', views.OrderCancelView.as_view(), name='order-cancel'),
    # path('<int:restaurant_pk>/order-items/<int:pk>/cancel/', views.OrderItemCancelView.as_view(), name='order-item-cancel'),
    # It a new Order Item
    # path('<int:restaurant_pk>/orderitem/list/', views.OrderItemListAPIView.as_view(), name='order-item-list'),
    # path('<int:restaurant_pk>/orderitem/detail/<int:pk>/', views.OrderItemDetail.as_view(), name='order-item-detail'),
    # path('<int:restaurant_pk>/orderitem/<int:order_pk>/create/', views.OrderItemCreateView.as_view(), name='orderitem-create'),
    # path('<int:restaurant_pk>/orderitem/<int:pk>/update/', views.OrderItemUpdateAPIView.as_view(), name='orderitem-update'),
    # path('<int:restaurant_pk>/orderitem/delete/<int:pk>/', views.OrderItemDeleteAPIView.as_view(), name='order-item-delete'),
    # Test Order management 2
    # path('<int:restaurant_pk>/orders/create2/', views.OrderCreateAPIView2.as_view(), name='order-create'),
    # path('<int:restaurant_pk>/orders/<int:pk>/update2/', views.OrderUpdateAPIView2.as_view(), name='order-update'),
    # path('<int:restaurant_id>/table/<int:table_id>/', views.get_orders_by_table, name='orders-by-table'),
    path('<int:restaurant_id>/table/<int:table_id>/latest/', views.get_latest_order_by_table, name='orders-by-table-latest'),
    # path('<int:restaurant_id>/table/<int:table_id>/create_or_update/', views.create_or_update_order, name='create-or-update-order'),
    path('<int:restaurant_id>/table/<int:table_id>/update_paid_status/', views.update_latest_order_paid_status, name='update-latest-order-paid-status'),
    # path('<int:restaurant_id>/table/<int:table_id>/pending-orders/', views.PendingOrdersByTableView.as_view(), name='pending-orders-by-table'),
    path('order-items/<int:pk>/status/', views.OrderItemStatusUpdateView.as_view(), name='update-order-item-status'),
    path('<int:restaurant_id>/tables-with-pending-orders/', views.TablesWithPendingOrdersView.as_view(), name='tables-with-pending-orders'),
    
]
