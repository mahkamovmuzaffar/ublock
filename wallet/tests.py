from django.test import TestCase

# Create your tests here.
# TODO: Add tests for wallet functionality, such as creating a wallet, adding funds, and making transactions.
# TODO: Test edge cases, such as insufficient funds and invalid transactions.   
# TODO: Use Django's testing framework to create unit tests for the wallet app. 

# Example test case for creating a wallet
def test_create_wallet(self):
    # Create a new wallet for a user
    wallet = Wallet.objects.create(user=self.user, balance=0)
    
    # Check that the wallet was created successfully
    self.assertIsNotNone(wallet)
    self.assertEqual(wallet.user, self.user)
    self.assertEqual(wallet.balance, 0)