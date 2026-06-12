from django.test import TestCase

from wallet.models import Wallet

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

# Example test case for adding funds to a wallet
def test_add_funds(self):    
    # Create a new wallet for a user
    wallet = Wallet.objects.create(user=self.user, balance=0)
    
    # Add funds to the wallet
    wallet.add_funds(100)
    
    # Check that the balance was updated correctly
    self.assertEqual(wallet.balance, 100)

def test_make_transaction(self):
    # Create two wallets for two users
    wallet1 = Wallet.objects.create(user=self.user1, balance=100)
    wallet2 = Wallet.objects.create(user=self.user2, balance=50)
    
    # Make a transaction from wallet1 to wallet2
    transaction = Transaction.objects.create(sender=wallet1, receiver=wallet2, amount=30)
    
    # Check that the transaction was created successfully
    self.assertIsNotNone(transaction)
    self.assertEqual(transaction.sender, wallet1)
    self.assertEqual(transaction.receiver, wallet2)
    self.assertEqual(transaction.amount, 30)
    
    # Check that the balances were updated correctly
    wallet1.refresh_from_db()
    wallet2.refresh_from_db()
    self.assertEqual(wallet1.balance, 70)
    self.assertEqual(wallet2.balance, 80)   

def test_insufficient_funds(self):
    # Create a wallet with insufficient funds
    wallet = Wallet.objects.create(user=self.user, balance=10)
    
    # Attempt to make a transaction that exceeds the balance
    with self.assertRaises(InsufficientFundsError):
        wallet.make_transaction(receiver_wallet, 20)   

def test_invalid_transaction(self):    
    # Create a wallet for a user
    wallet = Wallet.objects.create(user=self.user, balance=100)
    
    # Attempt to make a transaction with an invalid receiver
    with self.assertRaises(InvalidTransactionError):
        wallet.make_transaction(None, 50)

def test_invalid_amount(self):     
    # Create a wallet for a user
    wallet = Wallet.objects.create(user=self.user, balance=100)
    
    # Attempt to make a transaction with an invalid amount
    with self.assertRaises(InvalidAmountError):
        wallet.make_transaction(receiver_wallet, -10)

def test_transaction_history(self): 
    # Create a wallet for a user
    wallet = Wallet.objects.create(user=self.user, balance=100)
    
    # Make a few transactions
    wallet.make_transaction(receiver_wallet, 20)
    wallet.make_transaction(receiver_wallet, 30)
    
    # Check that the transaction history is correct
    history = wallet.get_transaction_history()
    self.assertEqual(len(history), 2)
    self.assertEqual(history[0].amount, 20)
    self.assertEqual(history[1].amount, 30)

def test_wallet_deletion(self):
    # Create a wallet for a user
    wallet = Wallet.objects.create(user=self.user, balance=100)
    
    # Delete the wallet
    wallet.delete()
    
    # Check that the wallet was deleted successfully
    self.assertFalse(Wallet.objects.filter(pk=wallet.pk).exists())  

def test_wallet_str(self):      
    # Create a wallet for a user
    wallet = Wallet.objects.create(user=self.user, balance=100)
    
    # Check the string representation of the wallet
    self.assertEqual(str(wallet), f"Wallet of {self.user.username} with balance {wallet.balance}")

def test_wallet_balance_update(self):   
    # Create a wallet for a user
    wallet = Wallet.objects.create(user=self.user, balance=100)
    
    # Update the balance of the wallet
    wallet.balance += 50
    wallet.save()
    
    # Check that the balance was updated correctly
    wallet.refresh_from_db()
    self.assertEqual(wallet.balance, 150)

def test_wallet_user_relation(self):        
    # Create a wallet for a user
    wallet = Wallet.objects.create(user=self.user, balance=100)
    
    # Check that the wallet is related to the correct user
    self.assertEqual(wallet.user, self.user)

def test_wallet_unique_user(self):
    # Create a wallet for a user
    wallet1 = Wallet.objects.create(user=self.user, balance=100)
    
    # Attempt to create another wallet for the same user
    with self.assertRaises(IntegrityError):
        Wallet.objects.create(user=self.user, balance=50)



def test_wallet_multiple_users(self):
    # Create wallets for multiple users
    wallet1 = Wallet.objects.create(user=self.user, balance=100)
    wallet2 = Wallet.objects.create(user=self.user2, balance=200)

    # Check that each wallet is related to the correct user
    self.assertEqual(wallet1.user, self.user)
    self.assertEqual(wallet2.user, self.user2)

def test_wallet_balance_negative(self):
    # Create a wallet for a user
    wallet = Wallet.objects.create(user=self.user, balance=100)

    # Attempt to set a negative balance
    with self.assertRaises(ValidationError):
        wallet.balance = -50
        wallet.save()