from django.conf import settings
from django.db import models


class Wallet(models.Model):
    """
    Represents a user's blockchain wallet for token holdings.
    """
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='wallets')
    wallet_address = models.CharField(max_length=42, unique=True)  # Ethereum address format
    network = models.CharField(max_length=50, default='ethereum')  # blockchain network
    balance = models.DecimalField(max_digits=36, decimal_places=18, default=0)
    locked_balance = models.DecimalField(max_digits=36, decimal_places=18, default=0)
    is_active = models.BooleanField(default=True)
    is_verified = models.BooleanField(default=False)  # verification status
    label = models.CharField(max_length=100, blank=True, null=True)  # optional wallet label
    description = models.TextField(blank=True, null=True)  # optional description
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} - {self.wallet_address}"

    @property
    def available_balance(self):
        """Calculate available balance (total - locked)"""
        return self.balance - self.locked_balance


class Token(models.Model):
    """
    Represents a known ERC-20 token contract on a specific network.
    One row per contract per network — shared across all users.
    """
    contract_address = models.CharField(max_length=42)
    symbol           = models.CharField(max_length=20)
    name             = models.CharField(max_length=100)
    decimals         = models.PositiveSmallIntegerField(default=18)
    network          = models.CharField(max_length=50, default='ethereum')
    logo_url         = models.URLField(blank=True, null=True)
    coingecko_id     = models.CharField(max_length=100, blank=True, null=True)
    is_verified      = models.BooleanField(default=False)
    created_at       = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('contract_address', 'network')
        ordering = ['symbol']

    def __str__(self):
        return f"{self.symbol} ({self.network})"


class WalletToken(models.Model):
    """
    Tracks a specific ERC-20 token for a wallet.
    Caches the last-fetched balance so we don't hit the chain on every request.
    """
    wallet         = models.ForeignKey(Wallet, on_delete=models.CASCADE, related_name='tokens')
    token          = models.ForeignKey(Token, on_delete=models.CASCADE, related_name='wallet_entries')
    balance        = models.DecimalField(max_digits=36, decimal_places=18, default=0)
    balance_usd    = models.DecimalField(max_digits=20, decimal_places=2, default=0)
    last_synced_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ('wallet', 'token')

    def __str__(self):
        return f"{self.wallet.wallet_address} — {self.token.symbol}"
