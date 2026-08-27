from django.db import models


class User(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    email = models.EmailField()
    password = models.CharField(max_length=255)
    role = models.CharField(max_length=50)
    created_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        managed = False
        db_table = "users"

    def __str__(self):
        return self.name


class Product(models.Model):
    id = models.AutoField(primary_key=True)

    name = models.CharField(max_length=150)

    description = models.TextField(
        null=True,
        blank=True
    )

    price = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    stock = models.IntegerField()

    images = models.TextField(
        null=True,
        blank=True
    )

    category = models.CharField(
        max_length=100
    )

    popularity = models.IntegerField()

    class Meta:
        managed = False
        db_table = "products"

    def __str__(self):
        return self.name


class Cart(models.Model):
    id = models.AutoField(primary_key=True)
    user_id = models.IntegerField()
    product_id = models.IntegerField()
    quantity = models.IntegerField()

    class Meta:
        managed = False
        db_table = "carts"

    def __str__(self):
        return f"Cart {self.id}"


class Order(models.Model):
    id = models.AutoField(primary_key=True)

    user_id = models.IntegerField()

    total_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    status = models.CharField(
        max_length=50
    )

    payment_status = models.CharField(
        max_length=50
    )

    class Meta:
        managed = False
        db_table = "orders"

    def __str__(self):
        return f"Order #{self.id}"


class OrderItem(models.Model):
    id = models.AutoField(primary_key=True)

    order_id = models.IntegerField()

    product_id = models.IntegerField()

    quantity = models.IntegerField()

    price = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    class Meta:
        managed = False
        db_table = "order_items"

    def __str__(self):
        return f"Order Item #{self.id}"


class Payment(models.Model):
    id = models.AutoField(primary_key=True)

    order_id = models.IntegerField()

    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    payment_method = models.CharField(
        max_length=50
    )

    transaction_id = models.CharField(
        max_length=255,
        null=True,
        blank=True
    )

    status = models.CharField(
        max_length=50
    )

    timestamp = models.DateTimeField()

    class Meta:
        managed = False
        db_table = "payments"

    def __str__(self):
        return f"Payment #{self.id}"