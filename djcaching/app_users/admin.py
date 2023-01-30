from django.contrib import admin
from .models import Address, BalanceModel


class AddressAdmin(admin.ModelAdmin):
    pass


class BalanceModelAdmin(admin.ModelAdmin):
    pass


admin.site.register(Address, AddressAdmin)
admin.site.register(BalanceModel, BalanceModelAdmin)
