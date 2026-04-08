from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class Wallet(models.Model):
    """
    Represents a user's blockchain wallet for token holdings.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='wallets')
    wallet_address = models.CharField(max_length=42, unique=True)  # Ethereum address format
    network = models.CharField(max_length=50, default='ethereum')  # blockchain network
    balance = models.DecimalField(max_digits=36, decimal_places=18, default=0)
    locked_balance = models.DecimalField(max_digits=36, decimal_places=18, default=0)
    is_active = models.BooleanField(default=True)
    is_verified = models.BooleanField(default=False)  # verification status
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} - {self.wallet_address}"

    @property
    def available_balance(self):
        """Calculate available balance (total - locked)"""
        return self.balance - self.locked_balance
