import json
import logging
import urllib.parse
import urllib.request
from decimal import Decimal

from django.core.cache import cache
from django.utils import timezone

logger = logging.getLogger(__name__)

# Minimal ERC-20 ABI — only the three read functions we need.
# An ABI (Application Binary Interface) tells Web3 how to encode
# function calls and decode return values for a smart contract.
ERC20_ABI = [
    {
        "constant": True,
        "inputs": [{"name": "_owner", "type": "address"}],
        "name": "balanceOf",
        "outputs": [{"name": "balance", "type": "uint256"}],
        "type": "function",
    },
    {
        "constant": True,
        "inputs": [],
        "name": "decimals",
        "outputs": [{"name": "", "type": "uint8"}],
        "type": "function",
    },
    {
        "constant": True,
        "inputs": [],
        "name": "symbol",
        "outputs": [{"name": "", "type": "string"}],
        "type": "function",
    },
]


def fetch_token_balance(rpc_url, wallet_address, contract_address, decimals):
    """
    Call the ERC-20 contract on-chain and return the human-readable balance.

    This is a READ-ONLY call — no gas cost, no private key needed.
    Web3 sends a JSON-RPC eth_call to the node, which executes balanceOf()
    locally and returns the result without creating a transaction.

    Args:
        rpc_url          — HTTP endpoint of the blockchain node (Infura, Alchemy, etc.)
        wallet_address   — the wallet whose balance we are querying
        contract_address — the ERC-20 token's smart contract address
        decimals         — how many decimal places this token uses (from Token.decimals)

    Returns:
        Decimal — human-readable balance (e.g. Decimal('123.456789'))

    Raises:
        RuntimeError if Web3 is not installed or the node is unreachable.
        ValueError   if either address is not a valid Ethereum address.
    """
    try:
        from web3 import Web3
    except ImportError:
        raise RuntimeError('web3 package is not installed. Run: pip install web3')

    # Step 1 — connect to the blockchain node via HTTP RPC
    w3 = Web3(Web3.HTTPProvider(rpc_url))
    if not w3.is_connected():
        raise RuntimeError(f'Unable to connect to RPC endpoint: {rpc_url}')

    # Step 2 — convert both addresses to EIP-55 checksum format.
    # Ethereum addresses are case-insensitive on-chain but Web3 enforces
    # checksum casing to catch typos (wrong casing = invalid address error).
    checksum_wallet   = Web3.to_checksum_address(wallet_address)
    checksum_contract = Web3.to_checksum_address(contract_address)

    # Step 3 — build a contract object.
    # This does NOT make a network call — it just gives Web3 a typed
    # interface to the contract using the ABI we defined above.
    contract = w3.eth.contract(address=checksum_contract, abi=ERC20_ABI)

    # Step 4 — call balanceOf(wallet_address) on the contract.
    # .call() sends an eth_call JSON-RPC request (read-only, free).
    # Returns a raw uint256 integer, e.g. 1000000 for 1.0 USDT (6 decimals).
    raw_balance = contract.functions.balanceOf(checksum_wallet).call()

    # Step 5 — convert raw integer to human-readable amount.
    # ERC-20 tokens store balances as integers scaled by 10**decimals.
    # USDT: raw=1_000_000,  decimals=6  → 1.000000 USDT
    # LINK: raw=5_000_000_000_000_000_000, decimals=18 → 5.0 LINK
    # We use Decimal throughout to avoid floating-point rounding errors.
    human_balance = Decimal(raw_balance) / Decimal(10 ** decimals)

    return human_balance


def fetch_token_metadata(rpc_url, contract_address):
    """
    Read symbol and decimals directly from an unknown ERC-20 contract.

    Used when a user adds a custom token by contract address — we don't
    need them to manually type the symbol or decimals; we read it from
    the chain instead.

    Args:
        rpc_url          — HTTP endpoint of the blockchain node
        contract_address — the ERC-20 token's smart contract address

    Returns:
        dict with keys: 'symbol' (str), 'decimals' (int)

    Raises:
        RuntimeError if Web3 is not installed or node is unreachable.
        Exception    if the contract does not implement ERC-20 (no symbol/decimals).
    """
    try:
        from web3 import Web3
    except ImportError:
        raise RuntimeError('web3 package is not installed. Run: pip install web3')

    # Step 1 — connect and validate the address
    w3 = Web3(Web3.HTTPProvider(rpc_url))
    if not w3.is_connected():
        raise RuntimeError(f'Unable to connect to RPC endpoint: {rpc_url}')

    checksum_contract = Web3.to_checksum_address(contract_address)

    # Step 2 — build a contract object with our minimal ABI
    contract = w3.eth.contract(address=checksum_contract, abi=ERC20_ABI)

    # Step 3 — read symbol() and decimals() from the contract.
    # These are standard ERC-20 read functions, always free to call.
    symbol   = contract.functions.symbol().call()
    decimals = contract.functions.decimals().call()

    return {'symbol': symbol, 'decimals': decimals}


def sync_wallet_token(wallet_token, rpc_url, usd_price=None):
    """
    Refresh the cached balance for a single WalletToken record.

    Fetches the live on-chain balance, optionally calculates USD value,
    then saves both back to the WalletToken row and stamps last_synced_at.

    Args:
        wallet_token — WalletToken model instance to update
        rpc_url      — HTTP endpoint of the blockchain node for this network
        usd_price    — current USD price of the token (Decimal or float), optional.
                       Pass None to skip USD calculation and leave balance_usd unchanged.

    Returns:
        Decimal — the updated human-readable balance
    """
    token = wallet_token.token

    # Step 1 — fetch fresh balance from the blockchain
    balance = fetch_token_balance(
        rpc_url=rpc_url,
        wallet_address=wallet_token.wallet.wallet_address,
        contract_address=token.contract_address,
        decimals=token.decimals,
    )

    # Step 2 — calculate USD value if a price was supplied
    balance_usd = wallet_token.balance_usd  # keep existing value by default
    if usd_price is not None:
        balance_usd = balance * Decimal(str(usd_price))

    # Step 3 — persist the updated balance and sync timestamp
    wallet_token.balance        = balance
    wallet_token.balance_usd    = balance_usd
    wallet_token.last_synced_at = timezone.now()
    wallet_token.save(update_fields=['balance', 'balance_usd', 'last_synced_at'])

    logger.info(
        'Synced %s balance for wallet %s: %s (≈ $%s)',
        token.symbol,
        wallet_token.wallet.wallet_address,
        balance,
        balance_usd,
    )

    return balance


# ── COINGECKO BASE URL ─────────────────────────────────────────────────────────
# Public API — no API key required for basic price lookups.
# Free tier limit: ~30 requests/minute. We cache all responses to stay well
# within that limit even under moderate traffic.
COINGECKO_BASE_URL = 'https://api.coingecko.com/api/v3'


def fetch_token_prices(coingecko_ids):
    """
    Fetch the current USD price for one or more tokens in a single API call.

    CoinGecko identifies tokens by a slug (e.g. 'tether', 'chainlink', 'uniswap').
    These are stored on the Token model as Token.coingecko_id.

    Args:
        coingecko_ids — list of CoinGecko slug strings, e.g. ['tether', 'chainlink']

    Returns:
        dict mapping each id to its USD price as a Decimal:
        { 'tether': Decimal('1.00'), 'chainlink': Decimal('14.23') }
        Tokens not found in the response are omitted from the result.

    Example usage:
        prices = fetch_token_prices(['tether', 'uniswap'])
        usdt_price = prices.get('tether', Decimal('0'))
    """
    # Step 1 — drop any ids that are empty or None (tokens without a CoinGecko id)
    valid_ids = [i for i in coingecko_ids if i]
    if not valid_ids:
        return {}

    # Step 2 — check the cache before hitting the network.
    # Key is built from sorted ids so ['tether','link'] and ['link','tether']
    # hit the same cache entry.
    cache_key = 'coingecko_prices:' + ','.join(sorted(valid_ids))
    cached = cache.get(cache_key)
    if cached is not None:
        return cached

    # Step 3 — build the request URL.
    # The /simple/price endpoint accepts a comma-separated list of ids
    # and returns their prices in the requested vs_currencies.
    params = urllib.parse.urlencode({
        'ids': ','.join(valid_ids),
        'vs_currencies': 'usd',
    })
    url = f'{COINGECKO_BASE_URL}/simple/price?{params}'

    # Step 4 — make the HTTP GET request.
    # We set a User-Agent header because CoinGecko blocks requests with none.
    # Timeout of 5 seconds — price data is not worth hanging a request thread for.
    req = urllib.request.Request(url, headers={'User-Agent': 'ublock-wallet/1.0'})
    try:
        with urllib.request.urlopen(req, timeout=5) as response:
            data = json.loads(response.read().decode())
    except Exception:
        logger.exception('CoinGecko price fetch failed for ids: %s', valid_ids)
        return {}

    # Step 5 — flatten the nested response into { id: Decimal(price) }.
    # Raw response looks like: { "tether": { "usd": 1.0 }, "chainlink": { "usd": 14.23 } }
    # We convert float → Decimal via str() to avoid floating-point precision loss.
    prices = {
        token_id: Decimal(str(info['usd']))
        for token_id, info in data.items()
        if 'usd' in info
    }

    # Step 6 — cache for 60 seconds so repeated requests within the same minute
    # don't count against the CoinGecko rate limit.
    cache.set(cache_key, prices, 60)

    logger.debug('Fetched CoinGecko prices for %s: %s', valid_ids, prices)
    return prices


def fetch_single_token_price(coingecko_id):
    """
    Convenience wrapper for fetching the price of one token.

    Args:
        coingecko_id — CoinGecko slug string, e.g. 'tether'

    Returns:
        Decimal price in USD, or Decimal('0') if not found.
    """
    if not coingecko_id:
        return Decimal('0')
    prices = fetch_token_prices([coingecko_id])
    return prices.get(coingecko_id, Decimal('0'))


def sync_wallet_token_with_price(wallet_token, rpc_url):
    """
    Full sync for a WalletToken — fetches balance AND current USD price together.

    This is the preferred function to call from views because it handles
    both blockchain and price API in one step, then saves everything.

    Args:
        wallet_token — WalletToken model instance to update
        rpc_url      — HTTP endpoint of the blockchain node for this network

    Returns:
        dict with 'balance' and 'balance_usd' as Decimals
    """
    token = wallet_token.token

    # Step 1 — fetch USD price from CoinGecko (cached, fast)
    usd_price = fetch_single_token_price(token.coingecko_id)

    # Step 2 — fetch on-chain balance and save everything via sync_wallet_token
    balance = sync_wallet_token(wallet_token, rpc_url, usd_price=usd_price)

    return {
        'balance': balance,
        'balance_usd': balance * usd_price,
    }
