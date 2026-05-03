from django.contrib import admin

from .models import Token, Wallet, WalletToken


@admin.register(Wallet)
class WalletAdmin(admin.ModelAdmin):
    list_display = ('wallet_address', 'user', 'network', 'balance', 'is_verified', 'is_active', 'created_at')
    list_filter = ('network', 'is_verified', 'is_active')
    search_fields = ('wallet_address', 'user__username', 'label')
    readonly_fields = ('created_at',)


@admin.register(Token)
class TokenAdmin(admin.ModelAdmin):
    list_display = ('symbol', 'name', 'network', 'contract_address', 'decimals', 'is_verified', 'created_at')
    list_filter = ('network', 'is_verified')
    search_fields = ('symbol', 'name', 'contract_address', 'coingecko_id')
    readonly_fields = ('created_at',)


@admin.register(WalletToken)
class WalletTokenAdmin(admin.ModelAdmin):
    list_display = ('wallet', 'token', 'balance', 'balance_usd', 'last_synced_at')
    list_filter = ('token__network',)
    search_fields = ('wallet__wallet_address', 'token__symbol')
    readonly_fields = ('last_synced_at',)
