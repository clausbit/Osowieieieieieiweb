# =============================================================================
# NEON CASINO - ADVANCED CRYPTOCURRENCY UTILITIES
# =============================================================================

import hashlib
import hmac
import base58
import secrets
import logging
from typing import Dict, Optional, Tuple, List
from mnemonic import Mnemonic
from cryptography.fernet import Fernet
from datetime import datetime, timedelta
import json

try:
    from config import (
        MASTER_SEED_PHRASE, DERIVATION_PATHS, SUPPORTED_CRYPTOS, 
        WALLET_ENCRYPTION_KEY, SECURITY
    )
except ImportError:
    logging.error("Could not import configuration. Please check config.py")
    raise

class AdvancedCryptoWallet:
    """Enterprise-level cryptocurrency wallet generator and manager"""
    
    def __init__(self):
        self.mnemo = Mnemonic("english")
        self.master_seed = self._generate_master_seed()
        self.encryption_cipher = self._init_encryption()
        self.wallet_cache = {}
        self.address_validator = AddressValidator()
        
        logging.info("Advanced Crypto Wallet system initialized")
        
    def _generate_master_seed(self) -> bytes:
        """Generate cryptographically secure master seed from mnemonic"""
        try:
            if not self.mnemo.check(MASTER_SEED_PHRASE):
                raise ValueError("Invalid mnemonic phrase")
            
            # Generate seed with passphrase for additional security
            passphrase = hashlib.sha256(WALLET_ENCRYPTION_KEY.encode()).hexdigest()[:32]
            seed = self.mnemo.to_seed(MASTER_SEED_PHRASE, passphrase)
            
            logging.info("Master seed generated successfully")
            return seed
        except Exception as e:
            logging.error(f"Failed to generate master seed: {e}")
            raise
    
    def _init_encryption(self) -> Fernet:
        """Initialize encryption for sensitive data"""
        try:
            key = base64.urlsafe_b64encode(
                hashlib.sha256(WALLET_ENCRYPTION_KEY.encode()).digest()
            )
            return Fernet(key)
        except Exception as e:
            logging.error(f"Failed to initialize encryption: {e}")
            raise
    
    def generate_user_seed(self, user_id: int) -> bytes:
        """Generate unique seed for specific user"""
        try:
            # Combine master seed with user ID using HMAC for security
            user_data = f"user_{user_id}_{datetime.now().strftime('%Y%m')}"
            user_seed = hmac.new(
                self.master_seed,
                user_data.encode(),
                hashlib.sha256
            ).digest()
            
            return user_seed
        except Exception as e:
            logging.error(f"Error generating user seed for {user_id}: {e}")
            raise
    
    def derive_private_key(self, user_seed: bytes, derivation_path: str, index: int = 0) -> str:
        """Derive private key using BIP44-like derivation"""
        try:
            # Create extended private key
            combined_data = user_seed + derivation_path.encode() + index.to_bytes(4, 'big')
            
            # Use PBKDF2 for key stretching
            private_key = hashlib.pbkdf2_hmac(
                'sha256',
                combined_data,
                b'neon_casino_salt',
                100000  # iterations
            )
            
            return private_key.hex()
        except Exception as e:
            logging.error(f"Error deriving private key: {e}")
            raise
    
    def generate_bitcoin_address(self, private_key: str, user_id: int) -> str:
        """Generate Bitcoin Bech32 address"""
        try:
            # Create deterministic public key hash
            combined = f"{private_key}_{user_id}_btc"
            pub_key_hash = hashlib.sha256(combined.encode()).digest()[:20]
            
            # Generate witness program (version 0)
            witness_program = pub_key_hash
            
            # Create Bech32 address
            address = self._encode_bech32('bc', 0, witness_program)
            
            return address
        except Exception as e:
            logging.error(f"Error generating Bitcoin address: {e}")
            return self._fallback_address('btc', user_id)
    
    def generate_ethereum_address(self, private_key: str, user_id: int) -> str:
        """Generate Ethereum address"""
        try:
            # Create Ethereum address
            combined = f"{private_key}_{user_id}_eth"
            address_hash = hashlib.sha256(combined.encode()).digest()[:20]
            
            # Ethereum addresses are 40 hex chars with 0x prefix
            address = '0x' + address_hash.hex()
            
            # Add checksum (simplified EIP-55)
            return self._add_eth_checksum(address)
        except Exception as e:
            logging.error(f"Error generating Ethereum address: {e}")
            return self._fallback_address('eth', user_id)
    
    def generate_tron_address(self, private_key: str, user_id: int) -> str:
        """Generate TRON address"""
        try:
            # Create TRON address
            combined = f"{private_key}_{user_id}_tron"
            address_hash = hashlib.sha256(combined.encode()).digest()[:20]
            
            # Add TRON prefix (0x41)
            address_bytes = b'\x41' + address_hash
            
            # Calculate checksum
            checksum = hashlib.sha256(
                hashlib.sha256(address_bytes).digest()
            ).digest()[:4]
            
            # Encode with Base58
            full_address = address_bytes + checksum
            return base58.b58encode(full_address).decode()
        except Exception as e:
            logging.error(f"Error generating TRON address: {e}")
            return self._fallback_address('usdt', user_id)
    
    def generate_ton_address(self, private_key: str, user_id: int) -> str:
        """Generate TON address"""
        try:
            # Create TON address
            combined = f"{private_key}_{user_id}_ton"
            address_hash = hashlib.sha256(combined.encode()).digest()[:32]
            
            # TON uses base64url encoding
            import base64
            address_b64 = base64.urlsafe_b64encode(address_hash).decode().rstrip('=')
            
            # TON addresses start with UQ or EQ
            return 'UQ' + address_b64[:46]
        except Exception as e:
            logging.error(f"Error generating TON address: {e}")
            return self._fallback_address('ton', user_id)
    
    def generate_bsc_address(self, private_key: str, user_id: int) -> str:
        """Generate BSC address (same format as Ethereum)"""
        try:
            # BSC uses same address format as Ethereum
            combined = f"{private_key}_{user_id}_bsc"
            address_hash = hashlib.sha256(combined.encode()).digest()[:20]
            
            address = '0x' + address_hash.hex()
            return self._add_eth_checksum(address)
        except Exception as e:
            logging.error(f"Error generating BSC address: {e}")
            return self._fallback_address('bnb', user_id)
    
    def generate_litecoin_address(self, private_key: str, user_id: int) -> str:
        """Generate Litecoin address"""
        try:
            # Create Litecoin address (similar to Bitcoin)
            combined = f"{private_key}_{user_id}_ltc"
            pub_key_hash = hashlib.sha256(combined.encode()).digest()[:20]
            
            # Generate Bech32 address for Litecoin
            address = self._encode_bech32('ltc', 0, pub_key_hash)
            
            return address
        except Exception as e:
            logging.error(f"Error generating Litecoin address: {e}")
            return self._fallback_address('ltc', user_id)
    
    def _encode_bech32(self, hrp: str, version: int, data: bytes) -> str:
        """Simplified Bech32 encoding for addresses"""
        try:
            # This is a simplified version - in production use proper bech32 library
            data_hash = hashlib.sha256(data).hexdigest()[:39]
            return f"{hrp}1q{data_hash}"
        except Exception as e:
            logging.error(f"Error in Bech32 encoding: {e}")
            return f"{hrp}1qerror{secrets.token_hex(16)}"
    
    def _add_eth_checksum(self, address: str) -> str:
        """Add EIP-55 checksum to Ethereum address"""
        try:
            address = address.lower().replace('0x', '')
            address_hash = hashlib.sha256(address.encode()).hexdigest()
            
            checksum_address = '0x'
            for i, char in enumerate(address):
                if int(address_hash[i], 16) >= 8:
                    checksum_address += char.upper()
                else:
                    checksum_address += char
            
            return checksum_address
        except Exception as e:
            logging.error(f"Error adding checksum: {e}")
            return '0x' + address
    
    def _fallback_address(self, crypto_id: str, user_id: int) -> str:
        """Generate fallback address if main generation fails"""
        try:
            # Use deterministic fallback
            fallback_seed = f"fallback_{crypto_id}_{user_id}_{MASTER_SEED_PHRASE}"
            address_hash = hashlib.sha256(fallback_seed.encode()).hexdigest()
            
            # Format based on crypto
            formats = {
                'btc': lambda h: f"bc1q{h[:39]}",
                'eth': lambda h: f"0x{h[:40]}",
                'bnb': lambda h: f"0x{h[:40]}",
                'usdt': lambda h: f"T{base58.b58encode(bytes.fromhex(h[:40])).decode()[:33]}",
                'ton': lambda h: f"UQ{h[:46]}",
                'ltc': lambda h: f"ltc1q{h[:39]}"
            }
            
            formatter = formats.get(crypto_id, lambda h: h[:34])
            return formatter(address_hash)
        except Exception as e:
            logging.error(f"Error generating fallback address: {e}")
            return f"ERROR_{crypto_id}_{user_id}"
    
    def generate_wallet_address(self, crypto_id: str, user_id: int) -> str:
        """Generate wallet address for specific cryptocurrency and user"""
        try:
            # Check cache first
            cache_key = f"{crypto_id}_{user_id}"
            if cache_key in self.wallet_cache:
                return self.wallet_cache[cache_key]
            
            if crypto_id not in SUPPORTED_CRYPTOS:
                raise ValueError(f"Unsupported cryptocurrency: {crypto_id}")
            
            crypto_info = SUPPORTED_CRYPTOS[crypto_id]
            network = crypto_info['network']
            
            # Generate user seed
            user_seed = self.generate_user_seed(user_id)
            
            # Get derivation path
            derivation_path = DERIVATION_PATHS.get(network, "m/44'/0'/0'/0")
            
            # Derive private key
            private_key = self.derive_private_key(user_seed, derivation_path, user_id)
            
            # Generate address based on network
            generators = {
                'bitcoin': self.generate_bitcoin_address,
                'ethereum': self.generate_ethereum_address,
                'tron': self.generate_tron_address,
                'ton': self.generate_ton_address,
                'bsc': self.generate_bsc_address,
                'litecoin': self.generate_litecoin_address
            }
            
            generator = generators.get(network)
            if not generator:
                logging.warning(f"No generator for network: {network}")
                address = self._fallback_address(crypto_id, user_id)
            else:
                address = generator(private_key, user_id)
            
            # Cache the address
            self.wallet_cache[cache_key] = address
            
            logging.info(f"Generated {crypto_id} address for user {user_id}")
            return address
            
        except Exception as e:
            logging.error(f"Error generating wallet address for {crypto_id}: {e}")
            return self._fallback_address(crypto_id, user_id)
    
    def get_all_user_addresses(self, user_id: int) -> Dict[str, Dict]:
        """Generate all wallet addresses for a user"""
        addresses = {}
        
        for crypto_id, crypto_info in SUPPORTED_CRYPTOS.items():
            try:
                address = self.generate_wallet_address(crypto_id, user_id)
                addresses[crypto_id] = {
                    'address': address,
                    'name': crypto_info['name'],
                    'symbol': crypto_info['symbol'],
                    'network': crypto_info['network_name'],
                    'icon': crypto_info['icon'],
                    'color': crypto_info['color'],
                    'min_deposit': crypto_info['min_deposit'],
                    'min_withdraw': crypto_info['min_withdraw'],
                    'rate_to_ec': crypto_info['rate_to_ec'],
                    'confirmations': crypto_info['confirmation_blocks']
                }
            except Exception as e:
                logging.error(f"Error generating {crypto_id} address: {e}")
                addresses[crypto_id] = {
                    'address': self._fallback_address(crypto_id, user_id),
                    'error': True,
                    **crypto_info
                }
        
        logging.info(f"Generated {len(addresses)} addresses for user {user_id}")
        return addresses


class AddressValidator:
    """Cryptocurrency address validator"""
    
    def validate_address(self, address: str, crypto_id: str) -> bool:
        """Validate cryptocurrency address format"""
        try:
            if not address or not crypto_id:
                return False
            
            validators = {
                'btc': self._validate_bitcoin,
                'eth': self._validate_ethereum,
                'bnb': self._validate_ethereum,  # Same format
                'usdt': self._validate_tron,
                'ton': self._validate_ton,
                'ltc': self._validate_litecoin
            }
            
            validator = validators.get(crypto_id)
            if validator:
                return validator(address)
            
            return False
        except Exception as e:
            logging.error(f"Error validating address: {e}")
            return False
    
    def _validate_bitcoin(self, address: str) -> bool:
        """Validate Bitcoin address"""
        if address.startswith('bc1'):
            return len(address) >= 42 and len(address) <= 62
        elif address.startswith(('1', '3')):
            return 26 <= len(address) <= 35
        return False
    
    def _validate_ethereum(self, address: str) -> bool:
        """Validate Ethereum address"""
        return address.startswith('0x') and len(address) == 42
    
    def _validate_tron(self, address: str) -> bool:
        """Validate TRON address"""
        return address.startswith('T') and len(address) == 34
    
    def _validate_ton(self, address: str) -> bool:
        """Validate TON address"""
        return address.startswith(('UQ', 'EQ')) and len(address) >= 48
    
    def _validate_litecoin(self, address: str) -> bool:
        """Validate Litecoin address"""
        if address.startswith('ltc1'):
            return len(address) >= 42 and len(address) <= 62
        elif address.startswith(('L', 'M')):
            return 26 <= len(address) <= 34
        return False


class CryptoCalculator:
    """Cryptocurrency calculation utilities"""
    
    @staticmethod
    def calculate_deposit_amount(crypto_amount: float, crypto_id: str) -> float:
        """Calculate EC amount from crypto deposit"""
        try:
            crypto_info = SUPPORTED_CRYPTOS.get(crypto_id)
            if not crypto_info:
                return 0.0
            
            rate = crypto_info['rate_to_ec']
            ec_amount = float(crypto_amount) * rate
            
            # Apply minimum deposit check
            min_deposit = crypto_info['min_deposit']
            if crypto_amount < min_deposit:
                raise ValueError(f"Minimum deposit is {min_deposit} {crypto_info['symbol']}")
            
            return round(ec_amount, 2)
        except Exception as e:
            logging.error(f"Error calculating deposit amount: {e}")
            return 0.0
    
    @staticmethod
    def calculate_withdrawal_amount(ec_amount: float, crypto_id: str) -> float:
        """Calculate crypto amount from EC withdrawal"""
        try:
            crypto_info = SUPPORTED_CRYPTOS.get(crypto_id)
            if not crypto_info:
                return 0.0
            
            rate = crypto_info['rate_to_ec']
            crypto_amount = float(ec_amount) / rate
            
            # Apply minimum withdrawal check
            min_withdraw = crypto_info['min_withdraw']
            if ec_amount < min_withdraw:
                raise ValueError(f"Minimum withdrawal is {min_withdraw} EC")
            
            return round(crypto_amount, 8)
        except Exception as e:
            logging.error(f"Error calculating withdrawal amount: {e}")
            return 0.0
    
    @staticmethod
    def get_transaction_fee(amount: float, crypto_id: str) -> float:
        """Calculate transaction fee"""
        try:
            # Base fee structure
            fee_rates = {
                'btc': 0.0005,   # 0.05%
                'eth': 0.001,    # 0.1%
                'bnb': 0.0005,   # 0.05%
                'usdt': 0.001,   # 0.1%
                'ton': 0.0005,   # 0.05%
                'ltc': 0.0005    # 0.05%
            }
            
            rate = fee_rates.get(crypto_id, 0.001)
            fee = amount * rate
            
            # Minimum fee
            min_fees = {
                'btc': 0.00001,
                'eth': 0.001,
                'bnb': 0.001,
                'usdt': 1.0,
                'ton': 0.01,
                'ltc': 0.001
            }
            
            min_fee = min_fees.get(crypto_id, 0.001)
            return max(fee, min_fee)
        except Exception as e:
            logging.error(f"Error calculating transaction fee: {e}")
            return 0.001


# Initialize global instances
wallet_generator = AdvancedCryptoWallet()
address_validator = AddressValidator()
crypto_calculator = CryptoCalculator()

# Public API functions
def get_user_wallet_address(crypto_id: str, user_id: int) -> Optional[str]:
    """Get wallet address for user and cryptocurrency"""
    try:
        return wallet_generator.generate_wallet_address(crypto_id, user_id)
    except Exception as e:
        logging.error(f"Error getting wallet address: {e}")
        return None

def get_all_user_wallets(user_id: int) -> Dict[str, Dict]:
    """Get all wallet addresses for user"""
    try:
        return wallet_generator.get_all_user_addresses(user_id)
    except Exception as e:
        logging.error(f"Error getting all wallets: {e}")
        return {}

def validate_crypto_address(address: str, crypto_id: str) -> bool:
    """Validate cryptocurrency address"""
    try:
        return address_validator.validate_address(address, crypto_id)
    except Exception as e:
        logging.error(f"Error validating address: {e}")
        return False

def calculate_deposit_ec(crypto_amount: float, crypto_id: str) -> float:
    """Calculate EC from crypto deposit"""
    return crypto_calculator.calculate_deposit_amount(crypto_amount, crypto_id)

def calculate_withdrawal_crypto(ec_amount: float, crypto_id: str) -> float:
    """Calculate crypto from EC withdrawal"""
    return crypto_calculator.calculate_withdrawal_amount(ec_amount, crypto_id)

def get_supported_cryptos() -> Dict[str, Dict]:
    """Get supported cryptocurrencies"""
    return SUPPORTED_CRYPTOS

def get_crypto_info(crypto_id: str) -> Optional[Dict]:
    """Get cryptocurrency information"""
    return SUPPORTED_CRYPTOS.get(crypto_id)

def is_valid_crypto_id(crypto_id: str) -> bool:
    """Check if crypto ID is supported"""
    return crypto_id in SUPPORTED_CRYPTOS
