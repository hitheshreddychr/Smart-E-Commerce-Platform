import csv

from django.shortcuts import render
from django.http import HttpResponse
from django.db.models import Sum

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter

from .models import User, Product, Order, OrderItem


def analytics_dashboard(request):

    # Total Sales
    total_sales = Order.objects.aggregate(
        total=Sum("total_amount")
    )["total"] or 0

    # Total Orders
    total_orders = Order.objects.count()

    # Total Products
    total_products = Product.objects.count()

    # Top Selling Products
    top_product_data = (
        OrderItem.objects
        .values("product_id")
        .annotate(
            total_quantity=Sum("quantity")
        )
        .order_by("-total_quantity")[:5]
    )

    top_products = []

    for item in top_product_data:
        try:
            product = Product.objects.get(
                id=item["product_id"]
            )

            top_products.append({
                "name": product.name,
                "quantity": item["total_quantity"],
            })

        except Product.DoesNotExist:
            pass

    # Low Stock Products
    low_stock_products = Product.objects.filter(
        stock__lt=10
    )

    # Revenue Data
    orders = Order.objects.order_by("id")

    revenue_labels = []
    revenue_data = []

    for order in orders:
        revenue_labels.append(f"Order {order.id}")
        revenue_data.append(float(order.total_amount))

    context = {
        "total_sales": total_sales,
        "total_orders": total_orders,
        "total_products": total_products,
        "top_products": top_products,
        "low_stock_products": low_stock_products,
        "revenue_labels": revenue_labels,
        "revenue_data": revenue_data,
    }

    return render(
        request,
        "dashboard/analytics.html",
        context
    )


def export_users_csv(request):
    response = HttpResponse(
        content_type="text/csv"
    )

    response["Content-Disposition"] = (
        'attachment; filename="users_report.csv"'
    )

    writer = csv.writer(response)

    writer.writerow([
        "ID",
        "Name",
        "Email",
        "Role",
        "Created At"
    ])

    users = User.objects.all()

    for user in users:
        writer.writerow([
            user.id,
            user.name,
            user.email,
            user.role,
            user.created_at
        ])

    return response


def export_orders_csv(request):
    response = HttpResponse(
        content_type="text/csv"
    )

    response["Content-Disposition"] = (
        'attachment; filename="orders_report.csv"'
    )

    writer = csv.writer(response)

    writer.writerow([
        "Order ID",
        "User ID",
        "Total Amount",
        "Status",
        "Payment Status"
    ])

    orders = Order.objects.all()

    for order in orders:
        writer.writerow([
            order.id,
            order.user_id,
            order.total_amount,
            order.status,
            order.payment_status
        ])

    return response


def export_sales_csv(request):
    response = HttpResponse(
        content_type="text/csv"
    )

    response["Content-Disposition"] = (
        'attachment; filename="sales_report.csv"'
    )

    writer = csv.writer(response)

    writer.writerow([
        "Order ID",
        "User ID",
        "Total Amount",
        "Order Status",
        "Payment Status"
    ])

    orders = Order.objects.filter(
        payment_status="paid"
    )

    for order in orders:
        writer.writerow([
            order.id,
            order.user_id,
            order.total_amount,
            order.status,
            order.payment_status
        ])

    return response


def export_users_pdf(request):
    response = HttpResponse(
        content_type="application/pdf"
    )

    response["Content-Disposition"] = (
        'attachment; filename="users_report.pdf"'
    )

    pdf = canvas.Canvas(
        response,
        pagesize=letter
    )

    pdf.setTitle("Users Report")

    pdf.drawString(
        50,
        750,
        "Smart E-Commerce Platform - Users Report"
    )

    y = 700

    users = User.objects.all()

    for user in users:

        user_data = (
            f"ID: {user.id} | "
            f"Name: {user.name} | "
            f"Email: {user.email} | "
            f"Role: {user.role}"
        )

        pdf.drawString(
            50,
            y,
            user_data
        )

        y -= 30

        # Create a new page if needed
        if y < 50:
            pdf.showPage()
            y = 750

    pdf.save()

    return response

def export_sales_pdf(request):
    response = HttpResponse(
        content_type="application/pdf"
    )

    response["Content-Disposition"] = (
        'attachment; filename="sales_report.pdf"'
    )

    pdf = canvas.Canvas(
        response,
        pagesize=letter
    )

    pdf.setTitle("Sales Report")

    pdf.drawString(
        50,
        750,
        "Smart E-Commerce Platform - Sales Report"
    )

    y = 700

    orders = Order.objects.filter(
        payment_status="paid"
    )

    for order in orders:

        sales_data = (
            f"Order ID: {order.id} | "
            f"User ID: {order.user_id} | "
            f"Amount: {order.total_amount} | "
            f"Status: {order.status}"
        )

        pdf.drawString(
            50,
            y,
            sales_data
        )

        y -= 30

        # Create a new page if needed
        if y < 50:
            pdf.showPage()
            y = 750

    pdf.save()

    return response

def export_orders_pdf(request):
    response = HttpResponse(
        content_type="application/pdf"
    )

    response["Content-Disposition"] = (
        'attachment; filename="orders_report.pdf"'
    )

    pdf = canvas.Canvas(
        response,
        pagesize=letter
    )

    pdf.setTitle("Orders Report")

    pdf.drawString(
        50,
        750,
        "Smart E-Commerce Platform - Orders Report"
    )

    y = 700

    orders = Order.objects.all()

    for order in orders:

        order_data = (
            f"Order ID: {order.id} | "
            f"User ID: {order.user_id} | "
            f"Amount: {order.total_amount} | "
            f"Status: {order.status} | "
            f"Payment: {order.payment_status}"
        )

        pdf.drawString(
            50,
            y,
            order_data
        )

        y -= 30

        # Create a new page if needed
        if y < 50:
            pdf.showPage()
            y = 750

    pdf.save()

    return response