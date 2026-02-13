from django.contrib import admin
from .models import Category, Product, Cart, CartItem, Order, ProductReview

class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'category', 'view_count', 'created_at')
    list_filter = ('category', 'created_at')
    search_fields = ('name', 'description')

admin.site.register(Category)
admin.site.register(Product, ProductAdmin)
admin.site.register(Cart)
admin.site.register(CartItem)
admin.site.register(Order)
admin.site.register(ProductReview)