"""
TOKEN ASSETS MODULE
===================
This module handles ERC-20 token tracking for user wallets.

BACKGROUND — what is an ERC-20 token?
    Every blockchain has a native coin (ETH on Ethereum, MATIC on Polygon, BNB on BSC).
    On top of that, developers deploy "smart contracts" that act like custom currencies.
    ERC-20 is the standard interface every such token contract must follow.
    Examples: USDT, USDC, LINK, UNI — all ERC-20 tokens on Ethereum.

    A token contract lives at a specific address (e.g. 0xdAC17F958D2ee523a2206206994597C13D831ec7 = USDT).
    To check someone's USDT balance you call that contract's `balanceOf(address)` function via Web3.

WHAT THIS MODULE MUST DO (in order of priority):
    1.  Define a Token model  — stores known token contracts (address, symbol, decimals, network).
    2.  Define a WalletToken model — links a Wallet to a Token it wants to track + caches balance.
    3.  Fetch on-chain balance — call the ERC-20 contract's balanceOf() using Web3.
    4.  Fetch token price     — call CoinGecko public API to get USD price per token.
    5.  Views                 — list tokens, add token to wallet, refresh balance, remove token.
    6.  URLs                  — wire the views.

HOW THE PIECES CONNECT:
    User → Wallet (one user, many wallets)
         → WalletToken (one wallet, many tracked tokens)
              → Token (the actual ERC-20 contract metadata)

DEPENDENCIES TO INSTALL:
    pip install web3          # already used in wallet/views.py
    pip install requests      # for CoinGecko price API (or use urllib, already imported)

===================================================================================
STEP 1 — MODELS  (put this in wallet/models.py or a dedicated tokens/models.py)
===================================================================================
"""

# ── WHY WE NEED Token ──────────────────────────────────────────────────────────
# Each ERC-20 contract has:
#   contract_address  — the on-chain address of the token smart contract
#   symbol            — ticker shown in the UI (e.g. "USDT")
#   name              — full name (e.g. "Tether USD")
#   decimals          — how many decimal places the token uses.
#                       USDT uses 6, most others use 18.
#                       Raw on-chain value must be divided by 10**decimals to get
#                       a human-readable amount.
#   network           — which chain this contract lives on (ethereum, polygon, …)
#   logo_url          — optional image URL for the UI
#   coingecko_id      — CoinGecko's identifier for price lookups (e.g. "tether")
#
# Token rows are shared across all users — one row per contract per network.

# from django.db import models
#
# class Token(models.Model):
#     contract_address = models.CharField(max_length=42)
#     symbol           = models.CharField(max_length=20)
#     name             = models.CharField(max_length=100)
#     decimals         = models.PositiveSmallIntegerField(default=18)
#     network          = models.CharField(max_length=50, default='ethereum')
#     logo_url         = models.URLField(blank=True, null=True)
#     coingecko_id     = models.CharField(max_length=100, blank=True, null=True)
#     is_verified      = models.BooleanField(default=False)  # admin-approved tokens
#     created_at       = models.DateTimeField(auto_now_add=True)
#
#     class Meta:
#         unique_together = ('contract_address', 'network')  # same address on two chains = two rows
#         ordering = ['symbol']
#
#     def __str__(self):
#         return f"{self.symbol} ({self.network})"


# ── WHY WE NEED WalletToken ────────────────────────────────────────────────────
# A wallet can track many tokens.
# WalletToken is the join table between Wallet and Token.
# It also caches the last-fetched balance so we don't hit the blockchain every request.
#
#   wallet          — which wallet owns this token position
#   token           — which ERC-20 contract
#   balance         — cached raw balance (in token units, NOT wei)
#   balance_usd     — cached USD value at last refresh
#   last_synced_at  — when the balance was last fetched from the chain

# class WalletToken(models.Model):
#     wallet         = models.ForeignKey('Wallet', on_delete=models.CASCADE, related_name='tokens')
#     token          = models.ForeignKey(Token, on_delete=models.CASCADE, related_name='wallet_entries')
#     balance        = models.DecimalField(max_digits=36, decimal_places=18, default=0)
#     balance_usd    = models.DecimalField(max_digits=20, decimal_places=2, default=0)
#     last_synced_at = models.DateTimeField(null=True, blank=True)
#
#     class Meta:
#         unique_together = ('wallet', 'token')  # a wallet tracks each token at most once
#
#     def __str__(self):
#         return f"{self.wallet.wallet_address} — {self.token.symbol}"


"""
===================================================================================
STEP 2 — ON-CHAIN BALANCE FETCH  (service function, not a view)
===================================================================================

HOW balanceOf() WORKS:
    Every ERC-20 contract exposes a read function:
        balanceOf(address owner) → uint256
    You call it with the wallet address and it returns the raw integer balance.
    To convert: human_balance = raw_balance / 10 ** token.decimals

THE ABI:
    To call a contract function with Web3 you need its ABI (Application Binary Interface).
    The ABI tells Web3 the function names, argument types, and return types.
    For balanceOf we only need the tiny ERC-20 ABI slice below.
    You do NOT need the full contract ABI — just the functions you call.
"""

# Minimal ERC-20 ABI — only the functions we actually use
ERC20_ABI = [
    # balanceOf: given an owner address, returns their token balance as a uint256
    {
        "constant": True,
        "inputs": [{"name": "_owner", "type": "address"}],
        "name": "balanceOf",
        "outputs": [{"name": "balance", "type": "uint256"}],
        "type": "function",
    },
    # decimals: returns how many decimal places this token uses (usually 18)
    {
        "constant": True,
        "inputs": [],
        "name": "decimals",
        "outputs": [{"name": "", "type": "uint8"}],
        "type": "function",
    },
    # symbol: returns the ticker string e.g. "USDT"
    {
        "constant": True,
        "inputs": [],
        "name": "symbol",
        "outputs": [{"name": "", "type": "string"}],
        "type": "function",
    },
]

# ── HOW TO IMPLEMENT fetch_token_balance ───────────────────────────────────────
#
# def fetch_token_balance(rpc_url, wallet_address, contract_address, decimals):
#     """
#     Call the ERC-20 contract on-chain and return the human-readable balance.
#
#     Steps:
#       1. Connect to the network via Web3 HTTPProvider using rpc_url.
#       2. Build a contract object using the contract_address + ERC20_ABI.
#       3. Call contract.functions.balanceOf(wallet_address).call()
#          — this is a READ call, no gas, no transaction needed.
#       4. Divide the raw integer by 10**decimals to get the real amount.
#       5. Return as Decimal for precision (avoid float rounding errors).
#     """
#     from decimal import Decimal
#     from web3 import Web3
#
#     w3 = Web3(Web3.HTTPProvider(rpc_url))
#     checksum_wallet  = Web3.to_checksum_address(wallet_address)
#     checksum_contract = Web3.to_checksum_address(contract_address)
#
#     contract = w3.eth.contract(address=checksum_contract, abi=ERC20_ABI)
#     raw_balance = contract.functions.balanceOf(checksum_wallet).call()
#
#     return Decimal(raw_balance) / Decimal(10 ** decimals)


"""
===================================================================================
STEP 3 — PRICE FETCH  (CoinGecko public API — no API key required)
===================================================================================

CoinGecko is a free public API for crypto prices.
Endpoint:
    GET https://api.coingecko.com/api/v3/simple/price
        ?ids=tether,usd-coin,chainlink
        &vs_currencies=usd

Response:
    {
        "tether":    {"usd": 1.00},
        "usd-coin":  {"usd": 0.9997},
        "chainlink": {"usd": 14.23}
    }

HOW TO MAP TOKENS TO COINGECKO IDs:
    Each Token row stores a coingecko_id (e.g. "tether" for USDT).
    Collect all coingecko_ids for the tokens being displayed, fetch in one
    batched API call, then match back to each WalletToken.

RATE LIMITS:
    Free tier: ~30 calls/minute.
    Cache prices in Django cache for 60 seconds to stay within limits.
"""

# ── HOW TO IMPLEMENT fetch_token_prices ────────────────────────────────────────
#
# def fetch_token_prices(coingecko_ids):
#     """
#     Fetch USD prices for a list of CoinGecko token IDs in a single request.
#     Returns a dict: { 'tether': 1.00, 'chainlink': 14.23, ... }
#
#     Steps:
#       1. Join the ids list into a comma-separated string.
#       2. Build the CoinGecko URL with urllib.parse.urlencode.
#       3. Make the HTTP GET request (urllib.request or requests library).
#       4. Parse the JSON response.
#       5. Flatten to { id: usd_price } for easy lookup.
#       6. Cache the result for 60 seconds to avoid hammering the API.
#     """
#     import json, urllib.parse, urllib.request
#     from django.core.cache import cache
#
#     cache_key = f"coingecko_prices:{'_'.join(sorted(coingecko_ids))}"
#     cached = cache.get(cache_key)
#     if cached:
#         return cached
#
#     params = urllib.parse.urlencode({
#         'ids': ','.join(coingecko_ids),
#         'vs_currencies': 'usd',
#     })
#     url = f"https://api.coingecko.com/api/v3/simple/price?{params}"
#     req = urllib.request.Request(url, headers={'User-Agent': 'ublock-wallet/1.0'})
#
#     with urllib.request.urlopen(req, timeout=5) as resp:
#         data = json.loads(resp.read().decode())
#
#     prices = {token_id: info['usd'] for token_id, info in data.items()}
#     cache.set(cache_key, prices, 60)
#     return prices


"""
===================================================================================
STEP 4 — VIEWS
===================================================================================

Endpoints to implement (all under /api/wallets/<wallet_id>/tokens/):

    GET    /                    — WalletTokenListView
        List all tokens tracked by this wallet with cached balance + USD value.

    POST   /                    — WalletTokenAddView
        Add a token to track. Body: { contract_address, network }
        Steps:
          1. Validate the contract_address is a valid Ethereum address.
          2. Look up or create the Token row (may need to call the contract
             to read symbol/decimals if not already in DB).
          3. Create WalletToken linking this wallet to the token.
          4. Trigger an initial balance fetch.

    POST   /<token_id>/refresh/ — WalletTokenRefreshView
        Refresh the on-chain balance for one token.
        Calls fetch_token_balance(), updates WalletToken.balance and balance_usd,
        sets last_synced_at = now().

    DELETE /<token_id>/         — WalletTokenRemoveView
        Stop tracking a token (delete the WalletToken row).
        Does NOT delete the Token row — other wallets may still track it.

AUTHENTICATION:
    All views require LoginRequiredMixin.
    All views must verify wallet.user == request.user before acting.
"""


"""
===================================================================================
STEP 5 — URLS  (add to wallet/urls.py once views are implemented)
===================================================================================

    from django.urls import path
    from . import token_views   # rename/split as appropriate

    urlpatterns += [
        path('wallets/<int:wallet_id>/tokens/',
             token_views.WalletTokenListView.as_view(),   name='wallet-token-list'),
        path('wallets/<int:wallet_id>/tokens/add/',
             token_views.WalletTokenAddView.as_view(),    name='wallet-token-add'),
        path('wallets/<int:wallet_id>/tokens/<int:token_id>/refresh/',
             token_views.WalletTokenRefreshView.as_view(), name='wallet-token-refresh'),
        path('wallets/<int:wallet_id>/tokens/<int:token_id>/',
             token_views.WalletTokenRemoveView.as_view(), name='wallet-token-remove'),
    ]
"""


"""
===================================================================================
STEP 6 — THINGS TO WATCH OUT FOR
===================================================================================

DECIMALS MATTER:
    USDT uses 6 decimals, not 18. Always read decimals from the contract
    or store it in the Token model. Never assume 18.

CHECKSUM ADDRESSES:
    Ethereum addresses are case-sensitive when used with Web3.
    Always call Web3.to_checksum_address() before passing an address
    to a contract call or storing it in the DB.

NETWORK MISMATCH:
    The same contract_address can exist on multiple networks with
    completely different tokens. Always store (contract_address, network)
    together — never just the address alone.

GAS-FREE READS:
    balanceOf() and other "view" functions are read-only.
    They do NOT cost gas and do NOT require a private key or transaction.
    Only state-changing functions (transfers, approvals) cost gas.

RATE LIMITS:
    Public RPC nodes (Infura free tier, Alchemy free tier) have rate limits.
    Cache on-chain responses for at least 30 seconds.
    For production, use a paid RPC plan or run your own node.
"""
