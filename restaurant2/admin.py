from django.contrib import admin
from .models import Category, Restaurant, Table, MenuItem, Order, OrderItem, Employee, OrderStatusHistory


admin.site.register(Restaurant)
admin.site.register(Category)
admin.site.register(Table)
admin.site.register(MenuItem)
admin.site.register(Order)
admin.site.register(OrderItem)
admin.site.register(Employee)
admin.site.register(OrderStatusHistory)