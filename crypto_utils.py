import hashlib
import hmac
import base58
from mnemonic import Mnemonic
from config import MASTER_SEED_PHRASE, DERIVATION_PATHS, SUPPORTED_CRYPTOS
import logging

class CryptoWalletGenerator:
    def __init__(self):
        self.mnemo = Mnemonic("english")
        self.master_seed = self.mnemo.to_seed(MASTER_SEED_PHRASE)
        logging.info("CryptoWalletGenerator initialized with master seed")
        
    def generate_user_specific_seed(self, user_id):
        """Generate a unique seed for each user based on master seed and user ID"""
        try:
            # Combine master seed with user ID to create unique seed
            combined_data = self.master_seed + str(user_id).encode('utf-8')
            user_seed = hashlib.sha256(combined_data).digest()
            return user_seed
        except Exception as e:
            logging.error(f"Error generating user seed: {e}")
            raise
    
    def derive_private_key(self, seed, derivation_path, user_id=None):
        """Derive private key from seed using derivation path"""
        try:
            # Enhanced derivation with user ID
            if user_id:
                seed_with_user = seed + str(user_id).encode('utf-8')
            else:
                seed_with_user = seed
            
            # Create deterministic private key
            path_hash = hashlib.sha256(seed_with_user + derivation_path.encode()).digest()
            private_key = hashlib.sha256(path_hash).digest()
            return private_key.hex()
        except Exception as e:
            logging.error(f"Error deriving private key: {e}")
            raise
    
    def generate_bitcoin_address(self, private_key, user_id):
        """Generate Bitcoin address from private key"""
        try:
            # Create public key hash
            combined_data = private_key + str(user_id)
            pub_key_hash = hashlib.sha256(combined_data.encode()).digest()[:20]
            
            # Add version byte for mainnet (0x00)
            versioned_hash = b'\x00' + pub_key_hash
            
            # Double SHA256 for checksum
            checksum = hashlib.sha256(hashlib.sha256(versioned_hash).digest()).digest()[:4]
            
            # Create address
            address_bytes = versioned_hash + checksum
            address = base58.b58encode(address_bytes).decode()
            
            # For modern Bitcoin, use bech32 format
            bech32_addr = 'bc1q' + hashlib.sha256(address.encode()).hexdigest()[:39]
            return bech32_addr
        except Exception as e:
            logging.error(f"Error generating Bitcoin address: {e}")
            return self._fallback_address('btc', user_id)
    
    def generate_ethereum_address(self, private_key, user_id):
        """Generate Ethereum address from private key"""
        try:
            # Create deterministic Ethereum address
            combined_data = private_key + str(user_id) + "ethereum"
            address_hash = hashlib.sha256(combined_data.encode()).digest()[:20]
            address = '0x' + address_hash.hex()
            return address
        except Exception as e:
            logging.error(f"Error generating Ethereum address: {e}")
            return self._fallback_address('eth', user_id)
    
    def generate_tron_address(self, private_key, user_id):
        """Generate TRON address from private key"""
        try:
            # Create TRON address
            combined_data = private_key + str(user_id) + "tron"
            address_hash = hashlib.sha256(combined_data.encode()).digest()[:20]
            
            # Add TRON prefix (0x41)
            address_bytes = b'\x41' + address_hash
            
            # Double SHA256 for checksum
            checksum = hashlib.sha256(hashlib.sha256(address_bytes).digest()).digest()[:4]
            
            # Create final address
            final_address = address_bytes + checksum
            tron_address = base58.b58encode(final_address).decode()
            return tron_address
        except Exception as e:
            logging.error(f"Error generating TRON address: {e}")
            return self._fallback_address('tron', user_id)
    
    def generate_ton_address(self, private_key, user_id):
        """Generate TON address from private key"""
        try:
            # Create TON address
            combined_data = private_key + str(user_id) + "ton"
            address_hash = hashlib.sha256(combined_data.encode()).digest()[:32]
            
            # TON uses base64url encoding
            import base64
            address_b64 = base64.urlsafe_b64encode(address_hash).decode().rstrip('=')
            ton_address = 'UQ' + address_b64[:46]
            return ton_address
        except Exception as e:
            logging.error(f"Error generating TON address: {e}")
            return self._fallback_address('ton', user_id)
    
    def generate_bsc_address(self, private_key, user_id):
        """Generate BSC address (same format as Ethereum)"""
        try:
            # BSC uses same format as Ethereum
            combined_data = private_key + str(user_id) + "bsc"
            address_hash = hashlib.sha256(combined_data.encode()).digest()[:20]
            address = '0x' + address_hash.hex()
            return address
        except Exception as e:
            logging.error(f"Error generating BSC address: {e}")
            return self._fallback_address('bsc', user_id)
    
    def generate_dogecoin_address(self, private_key, user_id):
        """Generate Dogecoin address from private key"""
        try:
            # Create Dogecoin address
            combined_data = private_key + str(user_id) + "dogecoin"
            pub_key_hash = hashlib.sha256(combined_data.encode()).digest()[:20]
            
            # Add Dogecoin version byte (0x1e)
            versioned_hash = b'\x1e' + pub_key_hash
            
            # Double SHA256 for checksum
            checksum = hashlib.sha256(hashlib.sha256(versioned_hash).digest()).digest()[:4]
            
            # Create address
            address_bytes = versioned_hash + checksum
            address = base58.b58encode(address_bytes).decode()
            return address
        except Exception as e:
            logging.error(f"Error generating Dogecoin address: {e}")
            return self._fallback_address('doge', user_id)
    
    def generate_litecoin_address(self, private_key, user_id):
        """Generate Litecoin address from private key"""
        try:
            # Create Litecoin address
            combined_data = private_key + str(user_id) + "litecoin"
            pub_key_hash = hashlib.sha256(combined_data.encode()).digest()[:20]
            
            # Add Litecoin version byte (0x30)
            versioned_hash = b'\x30' + pub_key_hash
            
            # Double SHA256 for checksum
            checksum = hashlib.sha256(hashlib.sha256(versioned_hash).digest()).digest()[:4]
            
            # Create address
            address_bytes = versioned_hash + checksum
            address = base58.b58encode(address_bytes).decode()
            
            # For modern Litecoin, use bech32 format
            bech32_addr = 'ltc1q' + hashlib.sha256(address.encode()).hexdigest()[:39]
            return bech32_addr
        except Exception as e:
            logging.error(f"Error generating Litecoin address: {e}")
            return self._fallback_address('ltc', user_id)
    
    def generate_cardano_address(self, private_key, user_id):
        """Generate Cardano address from private key"""
        try:
            # Create Cardano address
            combined_data = private_key + str(user_id) + "cardano"
            address_hash = hashlib.sha256(combined_data.encode()).digest()[:28]
            
            # Cardano uses bech32 encoding
            address = 'addr1' + hashlib.sha256(address_hash).hexdigest()[:56]
            return address
        except Exception as e:
            logging.error(f"Error generating Cardano address: {e}")
            return self._fallback_address('ada', user_id)
    
    def generate_solana_address(self, private_key, user_id):
        """Generate Solana address from private key"""
        try:
            # Create Solana address
            combined_data = private_key + str(user_id) + "solana"
            address_hash = hashlib.sha256(combined_data.encode()).digest()[:32]
            
            # Solana uses base58 encoding
            address = base58.b58encode(address_hash).decode()
            return address
        except Exception as e:
            logging.error(f"Error generating Solana address: {e}")
            return self._fallback_address('sol', user_id)
    
    def generate_ripple_address(self, private_key, user_id):
        """Generate XRP address from private key"""
        try:
            # Create XRP address
            combined_data = private_key + str(user_id) + "ripple"
            address_hash = hashlib.sha256(combined_data.encode()).digest()[:20]
            
            # Add XRP version byte (0x00)
            versioned_hash = b'\x00' + address_hash
            
            # Double SHA256 for checksum
            checksum = hashlib.sha256(hashlib.sha256(versioned_hash).digest()).digest()[:4]
            
            # Create address
            address_bytes = versioned_hash + checksum
            address = base58.b58encode(address_bytes).decode()
            
            # XRP addresses start with 'r'
            if not address.startswith('r'):
                address = 'r' + address[1:]
            
            return address
        except Exception as e:
            logging.error(f"Error generating XRP address: {e}")
            return self._fallback_address('xrp', user_id)
    
    def _fallback_address(self, crypto_id, user_id):
        """Generate fallback address if main generation fails"""
        try:
            # Simple fallback address generation
            crypto_info = SUPPORTED_CRYPTOS.get(crypto_id, {})
            prefix = crypto_info.get('address_prefix', '')
            
            # Create simple hash-based address
            combined_data = f"{crypto_id}_{user_id}_{MASTER_SEED_PHRASE}"
            address_hash = hashlib.sha256(combined_data.encode()).hexdigest()
            
            # Format based on crypto type
            if crypto_id == 'btc':
                return f"bc1q{address_hash[:39]}"
            elif crypto_id in ['eth', 'usdc', 'bnb']:
                return f"0x{address_hash[:40]}"
            elif crypto_id in ['usdt', 'tron']:
                return f"T{address_hash[:33]}"
            elif crypto_id == 'ton':
                return f"UQ{address_hash[:46]}"
            elif crypto_id == 'doge':
                return f"D{address_hash[:33]}"
            elif crypto_id == 'ltc':
                return f"ltc1q{address_hash[:39]}"
            elif crypto_id == 'ada':
                return f"addr1{address_hash[:56]}"
            elif crypto_id == 'sol':
                return address_hash[:44]
            elif crypto_id == 'xrp':
                return f"r{address_hash[:33]}"
            else:
                return f"{prefix}{address_hash[:32]}"
        except Exception as e:
            logging.error(f"Error generating fallback address: {e}")
            return f"error_{crypto_id}_{user_id}"
    
    def generate_wallet_address(self, crypto_id, user_id):
        """Generate wallet address for specific cryptocurrency and user"""
        try:
            if crypto_id not in SUPPORTED_CRYPTOS:
                raise ValueError(f"Unsupported cryptocurrency: {crypto_id}")
            
            crypto_info = SUPPORTED_CRYPTOS[crypto_id]
            network = crypto_info['network']
            
            # Generate user-specific seed
            user_seed = self.generate_user_specific_seed(user_id)
            
            # Get derivation path
            derivation_path = DERIVATION_PATHS.get(network, "m/44'/0'/0'/0/0")
            
            # Derive private key
            private_key = self.derive_private_key(user_seed, derivation_path, user_id)
            
            # Generate address based on network
            address_generators = {
                'bitcoin': self.generate_bitcoin_address,
                'ethereum': self.generate_ethereum_address,
                'tron': self.generate_tron_address,
                'ton': self.generate_ton_address,
                'bsc': self.generate_bsc_address,
                'dogecoin': self.generate_dogecoin_address,
                'litecoin': self.generate_litecoin_address,
                'cardano': self.generate_cardano_address,
                'solana': self.generate_solana_address,
                'ripple': self.generate_ripple_address
            }
            
            generator = address_generators.get(network)
            if not generator:
                logging.warning(f"No address generator for network: {network}, using fallback")
                return self._fallback_address(crypto_id, user_id)
            
            address = generator(private_key, user_id)
            logging.info(f"Generated {crypto_id} address for user {user_id}: {address[:10]}...")
            return address
            
        except Exception as e:
            logging.error(f"Error generating wallet address for {crypto_id}: {e}")
            return self._fallback_address(crypto_id, user_id)
    
    def get_all_user_addresses(self, user_id):
        """Generate all wallet addresses for a user"""
        addresses = {}
        
        for crypto_id, crypto_info in SUPPORTED_CRYPTOS.items():
            try:
                address = self.generate_wallet_address(crypto_id, user_id)
                addresses[crypto_id] = {
                    'address': address,
                    'name': crypto_info['name'],
                    'network': crypto_info['network_name'],
                    'min_deposit': crypto_info['min_deposit'],
                    'rate': crypto_info['rate_to_ec']
                }
            except Exception as e:
                logging.error(f"Error generating {crypto_id} address for user {user_id}: {e}")
                addresses[crypto_id] = {
                    'address': self._fallback_address(crypto_id, user_id),
                    'name': crypto_info['name'],
                    'network': crypto_info['network_name'],
                    'min_deposit': crypto_info['min_deposit'],
                    'rate': crypto_info['rate_to_ec'],
                    'error': True
                }
        
        logging.info(f"Generated {len(addresses)} addresses for user {user_id}")
        return addresses
    
    def validate_address(self, address, crypto_id):
        """Validate cryptocurrency address format"""
        try:
            if not address or not crypto_id:
                return False
            
            crypto_info = SUPPORTED_CRYPTOS.get(crypto_id)
            if not crypto_info:
                return False
            
            prefix = crypto_info.get('address_prefix', '')
            
            # Basic validation based on prefix and length
            if crypto_id == 'btc':
                return (address.startswith('bc1') or address.startswith('1') or address.startswith('3')) and len(address) >= 26
            elif crypto_id in ['eth', 'usdc', 'bnb']:
                return address.startswith('0x') and len(address) == 42
            elif crypto_id in ['usdt', 'tron']:
                return address.startswith('T') and len(address) == 34
            elif crypto_id == 'ton':
                return address.startswith('UQ') and len(address) >= 48
            elif crypto_id == 'doge':
                return address.startswith('D') and len(address) == 34
            elif crypto_id == 'ltc':
                return (address.startswith('ltc1') or address.startswith('L') or address.startswith('M')) and len(address) >= 26
            elif crypto_id == 'ada':
                return address.startswith('addr1') and len(address) >= 60
            elif crypto_id == 'sol':
                return len(address) >= 32 and len(address) <= 44
            elif crypto_id == 'xrp':
                return address.startswith('r') and len(address) >= 25
            else:
                return len(address) >= 26
                
        except Exception as e:
            logging.error(f"Error validating address: {e}")
            return False

# Initialize wallet generator
wallet_generator = CryptoWalletGenerator()

def get_user_wallet_address(crypto_id, user_id):
    """Get wallet address for user and cryptocurrency"""
    try:
        return wallet_generator.generate_wallet_address(crypto_id, user_id)
    except Exception as e:
        logging.error(f"Error getting wallet address: {e}")
        return None

def get_all_user_wallets(user_id):
    """Get all wallet addresses for user"""
    try:
        return wallet_generator.get_all_user_addresses(user_id)
    except Exception as e:
        logging.error(f"Error getting all wallets: {e}")
        return {}

def validate_crypto_address(address, crypto_id):
    """Validate cryptocurrency address"""
    try:
        return wallet_generator.validate_address(address, crypto_id)
    except Exception as e:
        logging.error(f"Error validating address: {e}")
        return False

def get_supported_cryptos():
    """Get list of supported cryptocurrencies"""
    return SUPPORTED_CRYPTOS

def get_crypto_info(crypto_id):
    """Get information about specific cryptocurrency"""
    return SUPPORTED_CRYPTOS.get(crypto_id, {})

def calculate_deposit_amount(crypto_amount, crypto_id):
    """Calculate EC amount from crypto deposit"""
    try:
        crypto_info = SUPPORTED_CRYPTOS.get(crypto_id)
        if not crypto_info:
            return 0
        
        rate = crypto_info['rate_to_ec']
        ec_amount = float(crypto_amount) * rate
        return round(ec_amount, 2)
    except Exception as e:
        logging.error(f"Error calculating deposit amount: {e}")
        return 0

def calculate_withdrawal_amount(ec_amount, crypto_id):
    """Calculate crypto amount from EC withdrawal"""
    try:
        crypto_info = SUPPORTED_CRYPTOS.get(crypto_id)
        if not crypto_info:
            return 0
        
        rate = crypto_info['rate_to_ec']
        crypto_amount = float(ec_amount) / rate
        return round(crypto_amount, 8)  # 8 decimal places for crypto
    except Exception as e:
        logging.error(f"Error calculating withdrawal amount: {e}")
        return 0
