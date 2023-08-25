from django.contrib import admin
from .models import *

class TransactionAdmin(admin.ModelAdmin):
    list_display = ['user', 'transaction_type', 'transaction_ref', 'amount','payment_at', 'ip_address']

admin.site.register(Transaction, TransactionAdmin)

admin.site.register(User)

admin.site.register(Tier)