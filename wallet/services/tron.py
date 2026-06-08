import logging
from decimal import Decimal

from django.utils import timezone

logger = logging.getLogger(__name__)


def _get_tron_client(node_url):
    try:
        from tronpy import Tron
        from tronpy.providers.http_provider import HTTPProvider
    except ImportError:
        raise RuntimeError('tronpy package is not installed. Run: pip install tronpy')

    return Tron(HTTPProvider(node_url))


def fetch_trc20_token_balance(node_url, wallet_address, contract_address, decimals):
    """
    Fetch the TRC-20 token balance for a wallet using a TRON node.

    Args:
        node_url         — HTTP endpoint of the TRON node (e.g. https://api.trongrid.io)
        wallet_address   — the wallet address to query
        contract_address — the TRC-20 contract address
        decimals         — number of decimals used by the token

    Returns:
        Decimal — human-readable token balance
    """
    client = _get_tron_client(node_url)
    contract = client.get_contract(contract_address)

    raw_balance = contract.functions.balanceOf(wallet_address)
    return Decimal(raw_balance) / Decimal(10 ** decimals)


def fetch_trc20_token_metadata(node_url, contract_address):
    """
    Read symbol and decimals from a TRC-20 contract.

    Args:
        node_url         — HTTP endpoint of the TRON node
        contract_address — the TRC-20 contract address

    Returns:
        dict with keys: 'symbol' (str), 'decimals' (int)
    """
    client = _get_tron_client(node_url)
    contract = client.get_contract(contract_address)

    symbol = contract.functions.symbol()
    decimals = contract.functions.decimals()

    return {'symbol': symbol, 'decimals': int(decimals)}


def sync_trc20_wallet_token(wallet_token, node_url, usd_price=None):
    """
    Refresh the cached balance for a single TRC-20 WalletToken record.

    Args:
        wallet_token — WalletToken model instance to update
        node_url     — HTTP endpoint of the TRON node
        usd_price    — current USD price of the token (Decimal or float), optional.

    Returns:
        Decimal — the updated human-readable balance
    """
    token = wallet_token.token

    balance = fetch_trc20_token_balance(
        node_url=node_url,
        wallet_address=wallet_token.wallet.wallet_address,
        contract_address=token.contract_address,
        decimals=token.decimals,
    )

    balance_usd = wallet_token.balance_usd
    if usd_price is not None:
        balance_usd = balance * Decimal(str(usd_price))

    wallet_token.balance = balance
    wallet_token.balance_usd = balance_usd
    wallet_token.last_synced_at = timezone.now()
    wallet_token.save(update_fields=['balance', 'balance_usd', 'last_synced_at'])

    logger.info(
        'Synced TRC-20 balance for wallet %s: %s (≈ $%s)',
        wallet_token.wallet.wallet_address,
        balance,
        balance_usd,
    )

    return balance
