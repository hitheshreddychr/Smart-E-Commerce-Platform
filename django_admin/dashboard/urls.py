from django.urls import path
from . import views

urlpatterns = [
    path("analytics/", views.analytics_dashboard, name="analytics"),
    path("reports/users/csv/", views.export_users_csv, name="export_users_csv"),
    path("reports/orders/csv/", views.export_orders_csv, name="export_orders_csv"),
    path("reports/sales/csv/", views.export_sales_csv, name="export_sales_csv"),
    path("reports/users/pdf/", views.export_users_pdf, name="export_users_pdf"),
    path("reports/orders/pdf/", views.export_orders_pdf, name="export_orders_pdf"),
    path("reports/sales/pdf/", views.export_sales_pdf, name="export_sales_pdf"),
]
    