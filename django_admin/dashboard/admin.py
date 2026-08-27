from django.contrib import admin
from .models import User, Product, Cart, Order, OrderItem, Payment

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "name",
        "email",
        "role",
        "created_at",
    )

    search_fields = (
        "name",
        "email",
    )

    list_filter = (
        "role",
    )


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "name",
        "category",
        "price",
        "stock",
        "popularity",
    )

    search_fields = (
        "name",
        "description",
        "category",
    )

    list_filter = (
        "category",
    )

@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "user_id",
        "product_id",
        "quantity",
    )

    search_fields = (
        "user_id",
        "product_id",
    )


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "user_id",
        "total_amount",
        "status",
        "payment_status",
    )

    list_filter = (
        "status",
        "payment_status",
    )

    search_fields = (
        "id",
        "user_id",
    )


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "order_id",
        "product_id",
        "quantity",
        "price",
    )

    search_fields = (
        "order_id",
        "product_id",
    )


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "order_id",
        "amount",
        "payment_method",
        "transaction_id",
        "status",
        "timestamp",
    )

    list_filter = (
        "status",
        "payment_method",
    )

    search_fields = (
        "order_id",
        "transaction_id",
    )