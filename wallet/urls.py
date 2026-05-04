from django.urls import path

from . import views

urlpatterns = [
    # Wallet CRUD
    path('', views.WalletListView.as_view(), name='wallet-list'),
    path('create/', views.WalletCreateView.as_view(), name='wallet-create'),
    path('<int:wallet_id>/', views.WalletDetailView.as_view(), name='wallet-detail'),
    path('<int:wallet_id>/update/', views.WalletUpdateView.as_view(), name='wallet-update'),
    path('<int:wallet_id>/delete/', views.WalletDeleteView.as_view(), name='wallet-delete'),
    path('<int:wallet_id>/verify/', views.WalletVerifyView.as_view(), name='wallet-verify'),
    path('<int:wallet_id>/link/', views.WalletLinkUserView.as_view(), name='wallet-link'),
    path('<int:wallet_id>/balance/', views.WalletBalanceView.as_view(), name='wallet-balance'),
    path('<int:wallet_id>/transactions/', views.WalletTransactionHistoryView.as_view(), name='wallet-transactions'),

    # Supported networks
    path('networks/', views.WalletNetworkListView.as_view(), name='wallet-networks'),

    # Token registry
    path('tokens/', views.TokenListView.as_view(), name='token-list'),
    path('tokens/<int:token_id>/', views.TokenDetailView.as_view(), name='token-detail'),

    # Per-wallet token management
    path('<int:wallet_id>/tokens/', views.WalletTokenListView.as_view(), name='wallet-token-list'),
    path('<int:wallet_id>/tokens/add/', views.WalletTokenAddView.as_view(), name='wallet-token-add'),
    path('<int:wallet_id>/tokens/<int:token_id>/remove/', views.WalletTokenRemoveView.as_view(), name='wallet-token-remove'),
    path('<int:wallet_id>/tokens/<int:token_id>/sync/', views.WalletTokenSyncView.as_view(), name='wallet-token-sync'),
]
