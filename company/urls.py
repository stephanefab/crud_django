from django.urls import path
from . import views

urlpatterns = [
    path("", views.home_view, name="company.index"),
    path("customers/", views.customers_list_view, name="company.customers"),
    path("customers/new", views.customers_create, name="company.customerCreate"),
    path("customers/<int:id>", views.customer_detail_view, name="company.customerDetail"),
    path("customers/update/<int:id>", views.customer_update, name="company.customerUpdate"),
    path("customers/delete/<int:id>", views.customer_delete, name="company.customerDelete"),
]