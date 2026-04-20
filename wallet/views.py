import json
import logging
import os
import secrets
import urllib.parse
import urllib.request
from datetime import datetime as dt_datetime

from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.cache import cache
from django.http import JsonResponse
from django.utils import timezone
from django.views import View

from .models import Wallet

try:
    from eth_keys import keys
    from web3 import Web3
except ImportError:
    keys = None
    Web3 = None

logger = logging.getLogger(__name__)


def _is_valid_eth_address(address):
    if Web3:
        return Web3.is_address(address)
    return (
        isinstance(address, str)
        and address.startswith('0x')
        and len(address) == 42
        and all(c in '0123456789abcdefABCDEF' for c in address[2:])
    )


# Wallet Management Views
class WalletListView(LoginRequiredMixin, View):
    """
    List all wallets for authenticated user or retrieve paginated wallets list.
    Returns wallet address, status, network, and verification status.
    """
    def get(self, request):
        try:
            wallets = Wallet.objects.filter(user=request.user, is_active=True)
            wallet_data = []
            for wallet in wallets:
                wallet_data.append({
                    'id': wallet.id,
                    'wallet_address': wallet.wallet_address,
                    'network': wallet.network,
                    'label': wallet.label,
                    'description': wallet.description,
                    'balance': str(wallet.balance),
                    'available_balance': str(wallet.available_balance),
                    'locked_balance': str(wallet.locked_balance),
                    'is_verified': wallet.is_verified,
                    'is_active': wallet.is_active,
                    'created_at': wallet.created_at.isoformat()
                })
            return JsonResponse({
                'success': True,
                'count': len(wallet_data),
                'wallets': wallet_data
            })
        except Exception:
            logger.exception('Failed to retrieve wallets for user %s', request.user.id)
            return JsonResponse({
                'success': False,
                'error': 'Failed to retrieve wallets'
            }, status=500)


class WalletCreateView(LoginRequiredMixin, View):
    """
    Create/Add a new wallet address for current user.
    Accepts wallet address, network type, and optional wallet label.
    """
    def post(self, request):
        try:
            data = json.loads(request.body)
            wallet_address = data.get('wallet_address')
            network = data.get('network', 'ethereum')
            label = data.get('label')
            description = data.get('description')

            if not wallet_address:
                return JsonResponse({
                    'success': False,
                    'error': 'Wallet address is required'
                }, status=400)

            if not _is_valid_eth_address(wallet_address):
                return JsonResponse({
                    'success': False,
                    'error': 'Invalid wallet address format'
                }, status=400)

            if Wallet.objects.filter(wallet_address=wallet_address).exists():
                return JsonResponse({
                    'success': False,
                    'error': 'Wallet address already exists'
                }, status=400)

            wallet = Wallet.objects.create(
                user=request.user,
                wallet_address=wallet_address,
                network=network,
                label=label,
                description=description
            )

            return JsonResponse({
                'success': True,
                'wallet': {
                    'id': wallet.id,
                    'wallet_address': wallet.wallet_address,
                    'network': wallet.network,
                    'label': wallet.label,
                    'description': wallet.description,
                    'balance': str(wallet.balance),
                    'available_balance': str(wallet.available_balance),
                    'locked_balance': str(wallet.locked_balance),
                    'is_verified': wallet.is_verified,
                    'is_active': wallet.is_active,
                    'created_at': wallet.created_at.isoformat()
                }
            }, status=201)

        except json.JSONDecodeError:
            return JsonResponse({
                'success': False,
                'error': 'Invalid JSON data'
            }, status=400)
        except Exception:
            logger.exception('Failed to create wallet for user %s', request.user.id)
            return JsonResponse({
                'success': False,
                'error': 'Failed to create wallet'
            }, status=500)


class WalletDetailView(LoginRequiredMixin, View):
    """
    Get detailed information about a specific wallet.
    Returns address, balance, network, verification status, and creation date.
    """
    def get(self, request, wallet_id):
        try:
            wallet = Wallet.objects.get(id=wallet_id, user=request.user, is_active=True)
            wallet_data = {
                'id': wallet.id,
                'wallet_address': wallet.wallet_address,
                'network': wallet.network,
                'label': wallet.label,
                'description': wallet.description,
                'balance': str(wallet.balance),
                'available_balance': str(wallet.available_balance),
                'locked_balance': str(wallet.locked_balance),
                'is_verified': wallet.is_verified,
                'is_active': wallet.is_active,
                'created_at': wallet.created_at.isoformat()
            }
            return JsonResponse({
                'success': True,
                'wallet': wallet_data
            })
        except Wallet.DoesNotExist:
            return JsonResponse({
                'success': False,
                'error': 'Wallet not found'
            }, status=404)
        except Exception:
            logger.exception('Failed to retrieve wallet %s', wallet_id)
            return JsonResponse({
                'success': False,
                'error': 'Failed to retrieve wallet details'
            }, status=500)


class WalletUpdateView(LoginRequiredMixin, View):
    """
    Update wallet metadata (label, description).
    Does NOT modify the blockchain address or network.
    """
    def put(self, request, wallet_id):
        try:
            wallet = Wallet.objects.get(id=wallet_id, user=request.user, is_active=True)
            data = json.loads(request.body)

            if 'label' in data:
                wallet.label = data['label']
            if 'description' in data:
                wallet.description = data['description']

            wallet.save()

            wallet_data = {
                'id': wallet.id,
                'wallet_address': wallet.wallet_address,
                'network': wallet.network,
                'label': wallet.label,
                'description': wallet.description,
                'balance': str(wallet.balance),
                'available_balance': str(wallet.available_balance),
                'locked_balance': str(wallet.locked_balance),
                'is_verified': wallet.is_verified,
                'is_active': wallet.is_active,
                'created_at': wallet.created_at.isoformat()
            }

            return JsonResponse({
                'success': True,
                'message': 'Wallet updated successfully',
                'wallet': wallet_data
            })

        except Wallet.DoesNotExist:
            return JsonResponse({
                'success': False,
                'error': 'Wallet not found'
            }, status=404)
        except json.JSONDecodeError:
            return JsonResponse({
                'success': False,
                'error': 'Invalid JSON data'
            }, status=400)
        except Exception:
            logger.exception('Failed to update wallet %s', wallet_id)
            return JsonResponse({
                'success': False,
                'error': 'Failed to update wallet'
            }, status=500)


class WalletDeleteView(LoginRequiredMixin, View):
    """
    Delete/remove a wallet from user's wallet list.
    May require additional verification before deletion.
    """
    def delete(self, request, wallet_id):
        try:
            wallet = Wallet.objects.get(id=wallet_id, user=request.user, is_active=True)
            wallet.is_active = False
            wallet.save()
            return JsonResponse({
                'success': True,
                'message': 'Wallet deleted successfully'
            })
        except Wallet.DoesNotExist:
            return JsonResponse({
                'success': False,
                'error': 'Wallet not found'
            }, status=404)
        except Exception:
            logger.exception('Failed to delete wallet %s', wallet_id)
            return JsonResponse({
                'success': False,
                'error': 'Failed to delete wallet'
            }, status=500)


class WalletVerifyView(LoginRequiredMixin, View):
    """
    Verify wallet ownership by signing a challenge message.
    Supports two-step verification:
    1. POST with 'action': 'request_challenge' - returns a challenge message to sign
    2. POST with 'action': 'verify_signature' - verifies the signed challenge
    """

    @staticmethod
    def _generate_challenge():
        return f"Verify wallet ownership - {secrets.token_hex(16)}"

    @staticmethod
    def _verify_signature(wallet_address, message, signature):
        if not Web3 or not keys:
            return False
        try:
            wallet_address = Web3.to_checksum_address(wallet_address)

            if signature.startswith('0x'):
                signature = signature[2:]

            signature_bytes = bytes.fromhex(signature)
            message_hash = Web3.keccak(text=message)

            if len(signature_bytes) == 65:
                v = signature_bytes[64]
                # Normalize legacy Ethereum v values (27/28 → 0/1)
                if v >= 27:
                    v -= 27
                r = int.from_bytes(signature_bytes[0:32], 'big')
                s = int.from_bytes(signature_bytes[32:64], 'big')

                sig = keys.Signature(vrs=(v, r, s))
                recovered_key = keys.PublicKey.recover_from_msg_hash(message_hash, sig)
                recovered_address = Web3.to_checksum_address(recovered_key.to_checksum_address())
                return recovered_address.lower() == wallet_address.lower()
        except Exception:
            logger.exception('Signature verification error for address %s', wallet_address)
            return False

        return False

    def _is_rate_limited(self, identifier):
        key = f'rate_limit:verify_challenge:{identifier}'
        count = cache.get(key, 0)
        if count >= 10:
            return True
        cache.set(key, count + 1, 900)
        return False

    def post(self, request, wallet_id=None):
        try:
            data = json.loads(request.body)
            action = data.get('action')

            if action == 'request_challenge':
                return self._request_challenge(request, wallet_id, data)
            elif action == 'verify_signature':
                return self._verify_signature_request(request, wallet_id, data)
            else:
                return JsonResponse({
                    'success': False,
                    'error': 'Invalid action. Use "request_challenge" or "verify_signature"'
                }, status=400)

        except json.JSONDecodeError:
            return JsonResponse({
                'success': False,
                'error': 'Invalid JSON data'
            }, status=400)
        except Exception:
            logger.exception('Wallet verification failed')
            return JsonResponse({
                'success': False,
                'error': 'Wallet verification failed'
            }, status=500)

    def _request_challenge(self, request, wallet_id, data):
        ip = request.META.get('REMOTE_ADDR', 'unknown')
        if self._is_rate_limited(ip):
            return JsonResponse({
                'success': False,
                'error': 'Too many challenge requests. Please try again later.'
            }, status=429)

        wallet_address = data.get('wallet_address')

        if not wallet_address:
            return JsonResponse({
                'success': False,
                'error': 'Wallet address is required'
            }, status=400)

        if not _is_valid_eth_address(wallet_address):
            return JsonResponse({
                'success': False,
                'error': 'Invalid wallet address format'
            }, status=400)

        try:
            Wallet.objects.get(wallet_address=wallet_address, user=request.user, is_active=True)
        except Wallet.DoesNotExist:
            return JsonResponse({
                'success': False,
                'error': 'Wallet not found'
            }, status=404)

        challenge = self._generate_challenge()
        cache_key = f"wallet_challenge_{wallet_address}"
        cache.set(cache_key, challenge, 900)

        return JsonResponse({
            'success': True,
            'challenge': challenge,
            'message': 'Please sign this message with your wallet private key',
            'expires_in': 900
        })

    def _verify_signature_request(self, request, wallet_id, data):
        wallet_address = data.get('wallet_address')
        signature = data.get('signature')

        if not wallet_address or not signature:
            return JsonResponse({
                'success': False,
                'error': 'Wallet address and signature are required'
            }, status=400)

        cache_key = f"wallet_challenge_{wallet_address}"
        challenge = cache.get(cache_key)

        if not challenge:
            return JsonResponse({
                'success': False,
                'error': 'No active challenge found. Request a new challenge first.'
            }, status=400)

        if not self._verify_signature(wallet_address, challenge, signature):
            return JsonResponse({
                'success': False,
                'error': 'Invalid signature. Wallet ownership verification failed.'
            }, status=401)

        cache.delete(cache_key)

        try:
            wallet = Wallet.objects.get(
                wallet_address=wallet_address,
                user=request.user,
                is_active=True
            )
            wallet.is_verified = True
            wallet.save()

            return JsonResponse({
                'success': True,
                'message': 'Wallet verified successfully',
                'wallet': {
                    'id': wallet.id,
                    'wallet_address': wallet.wallet_address,
                    'network': wallet.network,
                    'label': wallet.label,
                    'is_verified': wallet.is_verified,
                    'verified_at': timezone.now().isoformat()
                }
            })
        except Wallet.DoesNotExist:
            return JsonResponse({
                'success': False,
                'error': 'Wallet not found in system'
            }, status=404)
        except Exception:
            logger.exception('Failed to complete wallet verification for %s', wallet_address)
            return JsonResponse({
                'success': False,
                'error': 'Failed to complete wallet verification'
            }, status=500)


class WalletLinkUserView(LoginRequiredMixin, View):
    """
    Link wallet to user account after verification.
    Associates blockchain wallet with Django user record.
    """
    def post(self, request, wallet_id):
        try:
            wallet = Wallet.objects.get(id=wallet_id, is_active=True)

            if wallet.user != request.user:
                return JsonResponse({
                    'success': False,
                    'error': 'Wallet is already linked to another user'
                }, status=403)

            if not wallet.is_verified:
                return JsonResponse({
                    'success': False,
                    'error': 'Wallet must be verified before linking'
                }, status=400)

            wallet_data = {
                'id': wallet.id,
                'wallet_address': wallet.wallet_address,
                'network': wallet.network,
                'label': wallet.label,
                'description': wallet.description,
                'balance': str(wallet.balance),
                'available_balance': str(wallet.available_balance),
                'locked_balance': str(wallet.locked_balance),
                'is_verified': wallet.is_verified,
                'is_active': wallet.is_active,
                'created_at': wallet.created_at.isoformat()
            }

            return JsonResponse({
                'success': True,
                'message': 'Wallet successfully linked to user account',
                'wallet': wallet_data
            })

        except Wallet.DoesNotExist:
            return JsonResponse({
                'success': False,
                'error': 'Wallet not found'
            }, status=404)
        except Exception:
            logger.exception('Failed to link wallet %s', wallet_id)
            return JsonResponse({
                'success': False,
                'error': 'Failed to link wallet'
            }, status=500)


class WalletBalanceView(LoginRequiredMixin, View):
    """
    Get current balance of a specific wallet.
    Fetches balance from blockchain network.
    """

    NETWORK_RPCS = {
        'ethereum': os.environ.get('ETH_RPC_URL', 'https://mainnet.infura.io/v3/YOUR_INFURA_PROJECT_ID'),
        'polygon': os.environ.get('POLYGON_RPC_URL', 'https://polygon-rpc.com/'),
        'bsc': os.environ.get('BSC_RPC_URL', 'https://bsc-dataseed1.binance.org/'),
        'arbitrum': os.environ.get('ARBITRUM_RPC_URL', 'https://arb1.arbitrum.io/rpc'),
        'optimism': os.environ.get('OPTIMISM_RPC_URL', 'https://mainnet.optimism.io'),
    }

    def get(self, request, wallet_id):
        try:
            wallet = Wallet.objects.get(id=wallet_id, user=request.user, is_active=True)

            rpc_url = self.NETWORK_RPCS.get(wallet.network.lower())
            if not rpc_url:
                return JsonResponse({
                    'success': False,
                    'error': f'Unsupported network: {wallet.network}'
                }, status=400)

            if not Web3:
                return JsonResponse({
                    'success': False,
                    'error': 'Web3 library not available'
                }, status=500)

            w3 = Web3(Web3.HTTPProvider(rpc_url))

            if not w3.is_connected():
                return JsonResponse({
                    'success': False,
                    'error': 'Unable to connect to blockchain network'
                }, status=500)

            checksum_address = Web3.to_checksum_address(wallet.wallet_address)
            balance_wei = w3.eth.get_balance(checksum_address)
            balance_eth = Web3.from_wei(balance_wei, 'ether')

            wallet.balance = balance_eth
            wallet.save(update_fields=['balance'])

            return JsonResponse({
                'success': True,
                'wallet_id': wallet.id,
                'wallet_address': wallet.wallet_address,
                'network': wallet.network,
                'balance': str(balance_eth),
                'balance_wei': str(balance_wei),
                'symbol': self._get_network_symbol(wallet.network),
                'last_updated': timezone.now().isoformat()
            })

        except Wallet.DoesNotExist:
            return JsonResponse({
                'success': False,
                'error': 'Wallet not found'
            }, status=404)
        except Exception:
            logger.exception('Failed to fetch balance for wallet %s', wallet_id)
            return JsonResponse({
                'success': False,
                'error': 'Failed to fetch wallet balance'
            }, status=500)

    def _get_network_symbol(self, network):
        symbols = {
            'ethereum': 'ETH',
            'polygon': 'MATIC',
            'bsc': 'BNB',
            'arbitrum': 'ETH',
            'optimism': 'ETH',
        }
        return symbols.get(network.lower(), 'TOKEN')


class WalletTransactionHistoryView(LoginRequiredMixin, View):
    """
    Get transaction history for a specific wallet.
    Returns paginated list of incoming and outgoing transactions with timestamps.
    """

    EXPLORER_APIS = {
        'ethereum': 'https://api.etherscan.io/api',
        'polygon': 'https://api.polygonscan.com/api',
        'bsc': 'https://api.bscscan.com/api',
        'arbitrum': 'https://api.arbiscan.io/api',
        'optimism': 'https://api-optimistic.etherscan.io/api',
    }

    EXPLORER_API_KEYS = {
        'ethereum': os.environ.get('ETHERSCAN_API_KEY', ''),
        'polygon': os.environ.get('POLYGONSCAN_API_KEY', ''),
        'bsc': os.environ.get('BSCSCAN_API_KEY', ''),
        'arbitrum': os.environ.get('ARBISCAN_API_KEY', ''),
        'optimism': os.environ.get('OPTIMISM_ETHERSCAN_API_KEY', ''),
    }

    def get(self, request, wallet_id):
        try:
            wallet = Wallet.objects.get(id=wallet_id, user=request.user, is_active=True)
        except Wallet.DoesNotExist:
            return JsonResponse({
                'success': False,
                'error': 'Wallet not found'
            }, status=404)

        try:
            page = int(request.GET.get('page', 1))
            page_size = min(int(request.GET.get('page_size', 10)), 100)
        except (ValueError, TypeError):
            return JsonResponse({
                'success': False,
                'error': 'page and page_size must be integers'
            }, status=400)

        if page < 1 or page_size < 1:
            return JsonResponse({
                'success': False,
                'error': 'page and page_size must be positive integers'
            }, status=400)

        explorer_url = self.EXPLORER_APIS.get(wallet.network.lower())
        if not explorer_url:
            return JsonResponse({
                'success': False,
                'error': f'Unsupported network: {wallet.network}'
            }, status=400)

        cache_key = f'tx_history:{wallet.id}:{page}:{page_size}'
        cached = cache.get(cache_key)
        if cached:
            return JsonResponse(cached)

        try:
            api_key = self.EXPLORER_API_KEYS.get(wallet.network.lower(), '')
            params = urllib.parse.urlencode({
                'module': 'account',
                'action': 'txlist',
                'address': wallet.wallet_address,
                'startblock': 0,
                'endblock': 99999999,
                'page': page,
                'offset': page_size,
                'sort': 'desc',
                'apikey': api_key,
            })

            req = urllib.request.Request(
                f'{explorer_url}?{params}',
                headers={'User-Agent': 'ublock-wallet/1.0'}
            )
            with urllib.request.urlopen(req, timeout=10) as response:
                data = json.loads(response.read().decode())

        except Exception:
            logger.exception('Explorer API request failed for wallet %s', wallet_id)
            return JsonResponse({
                'success': False,
                'error': 'Failed to fetch transaction history'
            }, status=502)

        if data.get('status') != '1' and data.get('message') != 'No transactions found':
            return JsonResponse({
                'success': False,
                'error': 'Failed to fetch transaction history from explorer',
                'message': data.get('message', '')
            }, status=502)

        raw_txs = data.get('result', [])
        if not isinstance(raw_txs, list):
            raw_txs = []

        transactions = []
        for tx in raw_txs:
            direction = (
                'incoming' if tx.get('to', '').lower() == wallet.wallet_address.lower()
                else 'outgoing'
            )
            value_wei = int(tx.get('value', 0))
            value_eth = Web3.from_wei(value_wei, 'ether') if Web3 else value_wei / 10**18
            transactions.append({
                'hash': tx.get('hash'),
                'block_number': tx.get('blockNumber'),
                'timestamp': dt_datetime.fromtimestamp(
                    int(tx.get('timeStamp', 0)), tz=timezone.utc
                ).isoformat(),
                'from': tx.get('from'),
                'to': tx.get('to'),
                'value': str(value_eth),
                'value_wei': str(value_wei),
                'gas': tx.get('gas'),
                'gas_used': tx.get('gasUsed'),
                'gas_price': tx.get('gasPrice'),
                'is_error': tx.get('isError') == '1',
                'direction': direction,
                'confirmations': tx.get('confirmations'),
            })

        response_data = {
            'success': True,
            'wallet_id': wallet.id,
            'wallet_address': wallet.wallet_address,
            'network': wallet.network,
            'page': page,
            'page_size': page_size,
            'count': len(transactions),
            'transactions': transactions,
        }
        cache.set(cache_key, response_data, 60)

        return JsonResponse(response_data)


class WalletNetworkListView(View):
    """
    Get list of supported blockchain networks.
    Returns available networks for wallet linking (Ethereum, Polygon, etc).
    """
    def get(self, request):
        pass
