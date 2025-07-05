import hashlib
import hmac
import base58
from mnemonic import Mnemonic
from config import MASTER_SEED_PHRASE, DERIVATION_PATHS, SUPPORTED_CRYPTOS

class CryptoWalletGenerator:
    def __init__(self):
        self.mnemo = Mnemonic("english")
        
    def generate_seed_from_mnemonic(self, mnemonic_phrase):
        """Generate seed from mnemonic phrase"""
        return self.mnemo.to_seed(mnemonic_phrase)
    
    def derive_private_key(self, seed, derivation_path):
        """Derive private key from seed using derivation path"""
        # Simplified derivation - in production use proper BIP32/BIP44 libraries
        path_hash = hashlib.sha256((str(seed) + derivation_path).encode()).digest()
        return path_hash.hex()
    
    def generate_bitcoin_address(self, private_key):
        """Generate Bitcoin address from private key"""
        # Simplified Bitcoin address generation
        # In production, use proper Bitcoin libraries like bitcoinlib
        pub_key_hash = hashlib.sha256(private_key.encode()).digest()[:20]
        address_bytes = b'\x00' + pub_key_hash
        checksum = hashlib.sha256(hashlib.sha256(address_bytes).digest()).digest()[:4]
        return base58.b58encode(address_bytes + checksum).decode()
    
    def generate_ethereum_address(self, private_key):
        """Generate Ethereum address from private key"""
        # Simplified Ethereum address generation
        # In production, use proper Ethereum libraries like web3.py
        address_hash = hashlib.sha256(private_key.encode()).digest()[:20]
        return '0x' + address_hash.hex()
    
    def generate_tron_address(self, private_key):
        """Generate TRON address from private key"""
        # Simplified TRON address generation
        address_hash = hashlib.sha256(private_key.encode()).digest()[:21]
        address_hash = b'\x41' + address_hash[:20]  # TRON prefix
        checksum = hashlib.sha256(hashlib.sha256(address_hash).digest()).digest()[:4]
        return base58.b58encode(address_hash + checksum).decode()
    
    def generate_ton_address(self, private_key):
        """Generate TON address from private key"""
        # Simplified TON address generation
        address_hash = hashlib.sha256(private_key.encode()).digest()
        return 'UQ' + base58.b58encode(address_hash[:32]).decode()[:44]
    
    def generate_dogecoin_address(self, private_key):
        """Generate Dogecoin address from private key"""
        # Similar to Bitcoin but with different prefix
        pub_key_hash = hashlib.sha256(private_key.encode()).digest()[:20]
        address_bytes = b'\x1e' + pub_key_hash  # Dogecoin prefix
        checksum = hashlib.sha256(hashlib.sha256(address_bytes).digest()).digest()[:4]
        return base58.b58encode(address_bytes + checksum).decode()
    
    def generate_litecoin_address(self, private_key):
        """Generate Litecoin address from private key"""
        # Similar to Bitcoin but with different prefix
        pub_key_hash = hashlib.sha256(private_key.encode()).digest()[:20]
        address_bytes = b'\x30' + pub_key_hash  # Litecoin prefix
        checksum = hashlib.sha256(hashlib.sha256(address_bytes).digest()).digest()[:4]
        return base58.b58encode(address_bytes + checksum).decode()
    
    def generate_wallet_address(self, crypto_id, user_id=None):
        """Generate wallet address for specific cryptocurrency"""
        if crypto_id not in SUPPORTED_CRYPTOS:
            raise ValueError(f"Unsupported cryptocurrency: {crypto_id}")
        
        crypto_info = SUPPORTED_CRYPTOS[crypto_id]
        network = crypto_info['network']
        
        # Generate unique seed for user (if user_id provided)
        seed_phrase = MASTER_SEED_PHRASE
        if user_id:
            seed_phrase += f" user{user_id}"
        
        seed = self.generate_seed_from_mnemonic(seed_phrase)
        derivation_path = DERIVATION_PATHS.get(network, "m/44'/0'/0'/0/0")
        private_key = self.derive_private_key(seed, derivation_path)
        
        # Generate address based on network
        address_generators = {
            'bitcoin': self.generate_bitcoin_address,
            'ethereum': self.generate_ethereum_address,
            'tron': self.generate_tron_address,
            'ton': self.generate_ton_address,
            'bsc': self.generate_ethereum_address,  # BSC uses Ethereum format
            'dogecoin': self.generate_dogecoin_address,
            'litecoin': self.generate_litecoin_address
        }
        
        generator = address_generators.get(network)
        if not generator:
            raise ValueError(f"No address generator for network: {network}")
        
        return generator(private_key)
    
    def get_all_user_addresses(self, user_id):
        """Generate all wallet addresses for a user"""
        addresses = {}
        for crypto_id in SUPPORTED_CRYPTOS.keys():
            try:
                addresses[crypto_id] = self.generate_wallet_address(crypto_id, user_id)
            except Exception as e:
                print(f"Error generating {crypto_id} address: {e}")
                addresses[crypto_id] = None
        return addresses

# Initialize wallet generator
wallet_generator = CryptoWalletGenerator()

def get_user_wallet_address(crypto_id, user_id):
    """Get wallet address for user and cryptocurrency"""
    return wallet_generator.generate_wallet_address(crypto_id, user_id)

def get_all_user_wallets(user_id):
    """Get all wallet addresses for user"""
    return wallet_generator.get_all_user_addresses(user_id)
