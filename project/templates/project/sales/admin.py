from django.contrib import admin
from .models import CustomUser, Product, SaleRecord, Customer

admin.site.register(CustomUser)
admin.site.register(Product)
admin.site.register(SaleRecord)
admin.site.register(Customer)
