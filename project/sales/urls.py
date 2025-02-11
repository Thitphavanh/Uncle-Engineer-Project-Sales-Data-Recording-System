from django.urls import path
from django.contrib.auth.views import LogoutView
from . import views

urlpatterns = [
    path("", views.home, name="home-page"),
    path('table-product/', views.table_product, name='table-product-page'),
    path('confirm-sale/<int:order_id>/', views.confirm_sale, name='confirm-sale-page'),
    path('delete-sale/<int:order_id>/', views.delete_sale, name='delete-sale-page'),
    path('cancel-sale/<int:order_id>/', views.cancel_sale, name='cancel-sale-page'),  # New cancel URL
    path("create/", views.create_sale_record, name="create-sale-record-page"),
    path("sales/edit/<int:sale_id>/", views.edit_sale_record, name="edit-sale-record-page"),
    path("register/", views.register, name="register-page"),
    path("login/", views.user_login, name="login-page"),
    path("logout/", views.user_logout, name="logout-page"),
    path("customers/", views.customer_list_dashboard, name="customer-list-dashboard-page"),
    path("add-customer/", views.add_customer, name="add-customer-page"),
    path("customer/edit/<int:customer_id>/", views.edit_customer, name="edit-customer-page"),
    path("customer/delete/<int:customer_id>/", views.delete_customer, name="delete-customer-page"),
    path('dashboard/', views.sales_dashboard, name='sales-dashboard-page'),
    # path('products/', views.products, name='products'),
    # path('product/<int:product_id>/', views.product_detail, name='product_detail'),
    # path('orders/', views.orders, name='orders'),
    # path('about/', views.about, name='about'),
    # path('services/', views.services, name='services'),
    # path('contact/', views.contact, name='contact'),
    # path('profile/', views.profile, name='profile'),
]
