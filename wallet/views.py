from django.shortcuts import render
from django.http import JsonResponse
from django.views import View
from django.views.decorators.http import require_http_methods
from django.utils.decorators import method_decorator
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils import timezone
from django.core.cache import cache
import json
import secrets
from .models import Wallet

try:
    from eth_keys import keys
    from eth_utils import to_bytes, keccak
    from web3 import Web3
except ImportError:
    # Fallback if web3 packages are not installed
    keys = None
    keccak = None
    Web3 = None


# Wallet Management Views
class WalletListView(LoginRequiredMixin, View):
    """
    List all wallets for authenticated user or retrieve paginated wallets list.
    Returns wallet address, status, network, and verification status.
    """
    def get(self, request):
        """
        Retrieve all wallets for the authenticated user.
        Returns paginated list with wallet details.
        """
        try:
            # Get all active wallets for the current user
            wallets = Wallet.objects.filter(user=request.user, is_active=True)

            # Prepare wallet data for response
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

        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': 'Failed to retrieve wallets',
                'message': str(e)
            }, status=500)


class WalletCreateView(LoginRequiredMixin, View):
    """
    Create/Add a new wallet address for current user.
    Accepts wallet address, network type, and optional wallet label.
    """
    def post(self, request):
        try:
            # Parse JSON data from request body
            data = json.loads(request.body)
            wallet_address = data.get('wallet_address')
            network = data.get('network', 'ethereum')
            label = data.get('label')
            description = data.get('description')

            # Validate wallet address
            if not wallet_address:
                return JsonResponse({
                    'success': False,
                    'error': 'Wallet address is required'
                }, status=400)

            # Basic validation for Ethereum address format
            if not (wallet_address.startswith('0x') and len(wallet_address) == 42 and all(c in '0123456789abcdefABCDEF' for c in wallet_address[2:])):
                return JsonResponse({
                    'success': False,
                    'error': 'Invalid wallet address format'
                }, status=400)

            # Check if wallet address already exists
            if Wallet.objects.filter(wallet_address=wallet_address).exists():
                return JsonResponse({
                    'success': False,
                    'error': 'Wallet address already exists'
                }, status=400)

            # Create new wallet
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
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': 'Failed to create wallet',
                'message': str(e)
            }, status=500)


class WalletDetailView(LoginRequiredMixin, View):
    """
    Get detailed information about a specific wallet.
    Returns address, balance, network, verification status, and creation date.
    """
    def get(self, request, wallet_id):
        try:
            # Get the specific wallet for the authenticated user
            wallet = Wallet.objects.get(id=wallet_id, user=request.user, is_active=True)

            # Prepare wallet data for response
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
                'success': True, #
                'wallet': wallet_data
            })

        except Wallet.DoesNotExist:
            return JsonResponse({
                'success': False,
                'error': 'Wallet not found'
            }, status=404)
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': 'Failed to retrieve wallet details',
                'message': str(e)
            }, status=500)


class WalletUpdateView(LoginRequiredMixin, View):
    """
    Update wallet metadata (label, description, or other non-address fields).
    Does NOT modify the actual blockchain address.
    """
    def put(self, request, wallet_id):
        try:
            # Get the specific wallet for the authenticated user
            wallet = Wallet.objects.get(id=wallet_id, user=request.user, is_active=True)

            # Parse JSON data from request body
            data = json.loads(request.body)

            # Update allowed fields
            if 'label' in data:
                wallet.label = data['label']
            if 'description' in data:
                wallet.description = data['description']
            if 'network' in data:
                wallet.network = data['network']

            # Save the updated wallet
            wallet.save()

            # Prepare updated wallet data for response
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
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': 'Failed to update wallet',
                'message': str(e)
            }, status=500)


class WalletDeleteView(LoginRequiredMixin, View):
    """
    Delete/remove a wallet from user's wallet list.
    May require additional verification before deletion.
    """
    def delete(self, request, wallet_id):
        try:
            # Get the specific wallet for the authenticated user
            wallet = Wallet.objects.get(id=wallet_id, user=request.user, is_active=True)

            # Soft delete by setting is_active to False
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
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': 'Failed to delete wallet',
                'message': str(e)
            }, status=500)


class WalletVerifyView(View):
    """
    Verify wallet ownership by signing a challenge message.
    Supports two-step verification:
    1. POST with 'action': 'request_challenge' - returns a challenge message to sign
    2. POST with 'action': 'verify_signature' - verifies the signed challenge
    """
    
    @staticmethod
    def _generate_challenge():
        """Generate a random challenge message for user to sign."""
        return f"Verify wallet ownership - {secrets.token_hex(16)}"
    
    @staticmethod
    def _verify_signature(wallet_address, message, signature):
        """
        Verify that the signature is valid for the message using the wallet address.
        Returns True if signature is valid, False otherwise.
        """
        if not Web3 or not keys:
            return False
        
        try:
            # Normalize wallet address
            wallet_address = Web3.to_checksum_address(wallet_address)
            
            # Remove '0x' prefix from signature if present
            if signature.startswith('0x'):
                signature = signature[2:]
            
            # Convert signature hex to bytes
            signature_bytes = bytes.fromhex(signature)
            
            # The message that was signed
            message_hash = Web3.keccak(text=message)
            
            # Recover the public key from signature
            # Ethereum signatures are typically 65 bytes (130 hex chars)
            if len(signature_bytes) == 65:
                v = signature_bytes[64]
                r = int.from_bytes(signature_bytes[0:32], 'big')
                s = int.from_bytes(signature_bytes[32:64], 'big')
                
                # Create signature object
                sig = keys.Signature(vrs=(v, r, s))
                
                # Recover public key
                recovered_key = keys.PublicKey.recover_from_msg_hash(message_hash, sig)
                recovered_address = Web3.to_checksum_address(recovered_key.to_checksum_address())
                
                return recovered_address.lower() == wallet_address.lower()
        except Exception as e:
            # Log error for debugging
            print(f"Signature verification error: {str(e)}")
            return False
        
        return False
    
    def post(self, request, wallet_id=None):
        """
        Handle wallet verification requests.
        POST with action 'request_challenge' or 'verify_signature'.
        """
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
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': 'Wallet verification failed',
                'message': str(e)
            }, status=500)
    
    def _request_challenge(self, request, wallet_id, data):
        """Generate and return a challenge for the user to sign."""
        try:
            wallet_address = data.get('wallet_address')
            
            if not wallet_address:
                return JsonResponse({
                    'success': False,
                    'error': 'Wallet address is required'
                }, status=400)
            
            # Validate Ethereum address format
            if not (wallet_address.startswith('0x') and len(wallet_address) == 42):
                return JsonResponse({
                    'success': False,
                    'error': 'Invalid wallet address format'
                }, status=400)
            
            # Generate challenge
            challenge = self._generate_challenge()
            
            # Store challenge in cache with 15-minute expiration
            cache_key = f"wallet_challenge_{wallet_address}"
            cache.set(cache_key, challenge, 900)  # 15 minutes
            
            return JsonResponse({
                'success': True,
                'challenge': challenge,
                'message': 'Please sign this message with your wallet private key',
                'expires_in': 900
            })
        
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': 'Failed to generate challenge',
                'message': str(e)
            }, status=500)
    
    def _verify_signature_request(self, request, wallet_id, data):
        """Verify the signed challenge and mark wallet as verified."""
        try:
            wallet_address = data.get('wallet_address')
            signature = data.get('signature')
            
            if not wallet_address or not signature:
                return JsonResponse({
                    'success': False,
                    'error': 'Wallet address and signature are required'
                }, status=400)
            
            # Retrieve stored challenge from cache
            cache_key = f"wallet_challenge_{wallet_address}"
            challenge = cache.get(cache_key)
            
            if not challenge:
                return JsonResponse({
                    'success': False,
                    'error': 'No active challenge found. Request a new challenge first.'
                }, status=400)
            
            # Verify the signature
            if not self._verify_signature(wallet_address, challenge, signature):
                return JsonResponse({
                    'success': False,
                    'error': 'Invalid signature. Wallet ownership verification failed.'
                }, status=401)
            
            # Clear the used challenge
            cache.delete(cache_key)
            
            # Update wallet verification status
            try:
                wallet = Wallet.objects.get(
                    wallet_address=wallet_address,
                    is_active=True
                )
                wallet.is_verified = True
                wallet.save()
                
                wallet_data = {
                    'id': wallet.id,
                    'wallet_address': wallet.wallet_address,
                    'network': wallet.network,
                    'label': wallet.label,
                    'is_verified': wallet.is_verified,
                    'verified_at': timezone.now().isoformat()
                }
                
                return JsonResponse({
                    'success': True,
                    'message': 'Wallet verified successfully',
                    'wallet': wallet_data
                })
            
            except Wallet.DoesNotExist:
                return JsonResponse({
                    'success': False,
                    'error': 'Wallet not found in system'
                }, status=404)
        
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': 'Signature verification failed',
                'message': str(e)
            }, status=500)


class WalletLinkUserView(LoginRequiredMixin, View):
    """
    Link wallet to user account after verification.
    Associates blockchain wallet with Django user record.
    """
    def post(self, request, wallet_id):
        try:
            # Load the wallet record and ensure it is active
            wallet = Wallet.objects.get(id=wallet_id, is_active=True)

            # Reject if another user already owns this wallet
            if wallet.user != request.user:
                return JsonResponse({
                    'success': False,
                    'error': 'Wallet is already linked to another user'
                }, status=403)

            # Reject if the wallet has not been verified yet
            if not wallet.is_verified:
                return JsonResponse({
                    'success': False,
                    'error': 'Wallet must be verified before linking'
                }, status=400)

            # Build the wallet payload to return after successful linking
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

            # Return success response once linking checks are complete
            return JsonResponse({
                'success': True,
                'message': 'Wallet successfully linked to user account',
                'wallet': wallet_data
            })

        except Wallet.DoesNotExist:
            # Wallet does not exist or is inactive
            return JsonResponse({
                'success': False,
                'error': 'Wallet not found'
            }, status=404)
        except Exception as e:
            # Unexpected error while attempting to link the wallet
            return JsonResponse({
                'success': False,
                'error': 'Failed to link wallet',
                'message': str(e)
            }, status=500) 
        




class WalletBalanceView(LoginRequiredMixin, View):
    """
    Get current balance of a specific wallet.
    Fetches balance from blockchain network.
    """

    # Network RPC configurations
    NETWORK_RPCS = {
        'ethereum': 'https://mainnet.infura.io/v3/YOUR_INFURA_PROJECT_ID',  # Replace with actual Infura ID or use public RPC
        'polygon': 'https://polygon-rpc.com/',
        'bsc': 'https://bsc-dataseed1.binance.org/',
        'arbitrum': 'https://arb1.arbitrum.io/rpc',
        'optimism': 'https://mainnet.optimism.io',
    }

    def get(self, request, wallet_id):
        try:
            # Get the specific wallet for the authenticated user
            wallet = Wallet.objects.get(id=wallet_id, user=request.user, is_active=True)

            # Get RPC URL for the network
            rpc_url = self.NETWORK_RPCS.get(wallet.network.lower())
            if not rpc_url:
                return JsonResponse({
                    'success': False,
                    'error': f'Unsupported network: {wallet.network}'
                }, status=400)

            # Check if Web3 is available
            if not Web3:
                return JsonResponse({
                    'success': False,
                    'error': 'Web3 library not available'
                }, status=500)

            # Connect to blockchain
            w3 = Web3(Web3.HTTPProvider(rpc_url))

            # Check connection
            if not w3.is_connected():
                return JsonResponse({
                    'success': False,
                    'error': 'Unable to connect to blockchain network'
                }, status=500)

            # Get balance from blockchain
            checksum_address = Web3.to_checksum_address(wallet.wallet_address)
            balance_wei = w3.eth.get_balance(checksum_address)

            # Convert wei to ether (or native token)
            balance_eth = Web3.from_wei(balance_wei, 'ether')

            # Update wallet balance in database
            wallet.balance = balance_eth
            wallet.save()

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
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': 'Failed to fetch wallet balance',
                'message': str(e)
            }, status=500)

    def _get_network_symbol(self, network):
        """Get the native token symbol for the network"""
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
        'ethereum': 'YOUR_ETHERSCAN_API_KEY',
        'polygon': 'YOUR_POLYGONSCAN_API_KEY',
        'bsc': 'YOUR_BSCSCAN_API_KEY',
        'arbitrum': 'YOUR_ARBISCAN_API_KEY',
        'optimism': 'YOUR_OPTIMISM_ETHERSCAN_API_KEY',
    }

    def get(self, request, wallet_id):
        try:
            wallet = Wallet.objects.get(id=wallet_id, user=request.user, is_active=True)

            # Pagination params
            page = int(request.GET.get('page', 1))
            page_size = min(int(request.GET.get('page_size', 10)), 100)

            explorer_url = self.EXPLORER_APIS.get(wallet.network.lower())
            if not explorer_url:
                return JsonResponse({
                    'success': False,
                    'error': f'Unsupported network: {wallet.network}'
                }, status=400)

            import urllib.request
            import urllib.parse

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
                import json as _json
                data = _json.loads(response.read().decode())

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
                    'timestamp': timezone.datetime.fromtimestamp(
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

            return JsonResponse({
                'success': True,
                'wallet_id': wallet.id,
                'wallet_address': wallet.wallet_address,
                'network': wallet.network,
                'page': page,
                'page_size': page_size,
                'count': len(transactions),
                'transactions': transactions,
            })

        except Wallet.DoesNotExist:
            return JsonResponse({
                'success': False,
                'error': 'Wallet not found'
            }, status=404)
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': 'Failed to fetch transaction history',
                'message': str(e)
            }, status=500)


class WalletNetworkListView(View):
    """
    Get list of supported blockchain networks.
    Returns available networks for wallet linking (Ethereum, Polygon, etc).
    """
    def get(self, request):
        pass
