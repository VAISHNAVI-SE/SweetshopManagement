# sweetshop_app/admin.py
from django.contrib import admin
from .models import Sweet, Purchase

@admin.register(Sweet)
class SweetAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'category', 'price', 'quantity', 'created_at')
    search_fields = ('name', 'category')

@admin.register(Purchase)
class PurchaseAdmin(admin.ModelAdmin):
    list_display = ('id', 'sweet', 'user', 'quantity', 'purchased_at')
    list_filter = ('purchased_at',)