# 🎰 NEON CASINO - EPIC CRYPTO GAMING PLATFORM

## Overview

**Neon Casino** is a professional-grade Telegram Mini App that provides an epic cryptocurrency casino experience with stunning neon visuals, multiple games, and enterprise-level security. Built for high-volume operations with advanced features like multi-level referrals, comprehensive crypto support, and real-time analytics.

## ✨ Key Features

### 🎮 Multiple Casino Games
- **🎰 Neon Roll** - Classic color betting with 3D rollers (Red/Blue: 2x, Green: 5x, Yellow: 45x)
- **🎲 Neon Dice** - Predict rolls 1-100 (Under/Over 50: 1.98x, Exactly 50: 99x)
- **🎰 Neon Slots** - Match symbols for wins (Cherry: 2x up to Jackpot: 100x)
- **📈 Neon Crash** - Cash out before the crash (up to 10x multiplier)

### 💎 Advanced Cryptocurrency Support
- **6 Major Cryptocurrencies**: TON, USDT (TRC20), Bitcoin, Ethereum, BNB, Litecoin
- **Secure Wallet Generation**: Deterministic addresses from master seed phrase
- **Real-time Exchange Rates**: Dynamic conversion to in-game currency (EC)
- **Instant Deposits**: Automatic credit upon confirmation
- **Secure Withdrawals**: Multi-signature security

### 🔐 Enterprise Security
- **Firebase Admin Integration**: Persistent cloud database
- **Rate Limiting**: Protection against abuse
- **Anti-fraud Detection**: Advanced security measures
- **Encrypted Communications**: End-to-end security
- **Secure Key Management**: Hardware-level encryption

### 👥 Advanced Referral System
- **3-Level Deep Tracking**: 5% → 2% → 1% commission structure
- **Real-time Analytics**: Track referral performance
- **Automated Payouts**: Instant commission distribution
- **Referral Dashboard**: Comprehensive statistics

### 🎯 Gamification Features
- **Daily Tasks**: Win games, place bets, wager amounts
- **Achievement System**: Unlock rewards for milestones
- **VIP Program**: Bronze → Silver → Gold → Platinum → Diamond
- **Streak Bonuses**: Daily login rewards
- **Leaderboards**: Compete with other players

### 🎨 Epic Visual Design
- **Neon Aesthetic**: Stunning cyberpunk-inspired design
- **3D Animations**: Smooth roller animations and effects
- **Responsive UI**: Perfect on all devices
- **Particle Effects**: Dynamic background animations
- **Glassmorphism**: Modern translucent design elements

## 🚀 Installation & Deployment

### Prerequisites
- Ubuntu 20.04+ or Debian 11+
- Root access
- Domain name with DNS configured
- Firebase project setup
- Telegram Bot Token

### Quick Start

1. **Clone the repository**:
```bash
git clone <repository-url>
cd neon-casino
```

2. **Configure Firebase**:
   - Place your `neonrollfirebase-service-account.json` file in the project root
   - Update `FIREBASE_PROJECT_ID` in `config.py`

3. **Update Configuration**:
   - Edit `config.py` with your bot token and domain
   - Customize game settings and crypto rates

4. **Run Installation**:
```bash
chmod +x start.sh
sudo ./start.sh
```

The script will automatically:
- Install all system dependencies
- Configure nginx with SSL
- Set up PostgreSQL and Redis
- Create systemd services
- Configure security and monitoring
- Start the casino bot

### Manual Configuration

#### Bot Token Setup
```python
# config.py
BOT_TOKEN = "YOUR_BOT_TOKEN_HERE"
WEB_APP_URL = "https://yourdomain.com"
```

#### Firebase Setup
```python
# config.py
FIREBASE_PROJECT_ID = "your-firebase-project"
```

#### Crypto Wallet Configuration
The system uses a master seed phrase to generate deterministic wallets:
```python
MASTER_SEED_PHRASE = "your twelve word seed phrase here"
```

## 🎮 Game Configuration

### Game Mechanics

#### Neon Roll
- **House Edge**: 2%
- **Min Bet**: 1 EC
- **Max Bet**: 1000 EC
- **Probabilities**: Red (44%), Blue (44%), Green (10%), Yellow (2%)

#### Neon Dice
- **House Edge**: 1%
- **Min Bet**: 1 EC  
- **Max Bet**: 2000 EC
- **Fair Algorithm**: Cryptographically secure random generation

#### Neon Slots
- **House Edge**: 5%
- **Min Bet**: 1 EC
- **Max Bet**: 500 EC
- **Symbol Weights**: Dynamically balanced for profitability

#### Neon Crash
- **House Edge**: 1%
- **Min Bet**: 1 EC
- **Max Bet**: 1500 EC
- **Crash Algorithm**: Provably fair random generation

### Customizing Game Settings

Edit `config.py` to modify game parameters:

```python
CASINO_GAMES = {
    'neon_roll': {
        'min_bet': 1.0,
        'max_bet': 1000.0,
        'colors': {
            'red': {'multiplier': 2.0, 'probability': 0.44},
            # ... customize probabilities and multipliers
        }
    }
}
```

## 💰 Cryptocurrency Integration

### Supported Networks
- **TON**: Native TON network
- **TRON**: USDT TRC20 tokens
- **Bitcoin**: Native Bitcoin network
- **Ethereum**: Native ETH and ERC20 tokens
- **BSC**: BNB and BEP20 tokens
- **Litecoin**: Native Litecoin network

### Wallet Security
- **Deterministic Generation**: BIP44-compatible derivation
- **User-Specific Keys**: Unique addresses per user
- **Encrypted Storage**: AES-256 encryption
- **Seed Phrase Backup**: Secure master key storage

### Adding New Cryptocurrencies

1. **Update config.py**:
```python
SUPPORTED_CRYPTOS['new_crypto'] = {
    'name': 'New Crypto',
    'network': 'new_network',
    'min_deposit': 1,
    'rate_to_ec': 100.0,
    # ... other parameters
}
```

2. **Add derivation path**:
```python
DERIVATION_PATHS['new_network'] = "m/44'/xxx'/0'/0"
```

3. **Implement wallet generator** in `crypto_utils.py`

## 📊 Analytics & Monitoring

### Real-time Metrics
- **Active Users**: Live player count
- **Game Statistics**: Win rates, popular games
- **Financial Metrics**: Deposits, withdrawals, house profit
- **Performance Monitoring**: Response times, error rates

### Database Structure

#### Users Collection
```json
{
  "user_id": 123456789,
  "username": "player1",
  "balance": 150.50,
  "total_wagered": 1500.00,
  "total_won": 1200.00,
  "vip_level": "silver",
  "referrer_id": 987654321,
  "crypto_wallets": { /* generated addresses */ },
  "game_stats": { /* per-game statistics */ }
}
```

#### Transactions Collection
```json
{
  "user_id": 123456789,
  "type": "deposit",
  "crypto_id": "ton",
  "amount": 100.0,
  "ec_amount": 245.0,
  "status": "completed",
  "timestamp": "2024-01-01T00:00:00Z"
}
```

### Backup & Recovery
- **Automated Backups**: Daily database snapshots
- **Point-in-time Recovery**: Restore to any previous state
- **Disaster Recovery**: Multi-region backup storage

## 🛡️ Security Features

### Bot Security
- **Rate Limiting**: 60 requests per minute per user
- **Input Validation**: Comprehensive parameter checking
- **SQL Injection Prevention**: Parameterized queries only
- **XSS Protection**: Output sanitization

### Infrastructure Security
- **SSL/TLS Encryption**: Full HTTPS enforcement
- **Firewall Configuration**: UFW with minimal open ports
- **Fail2ban**: Automatic IP blocking for suspicious activity
- **Security Headers**: HSTS, CSP, X-Frame-Options

### Financial Security
- **Multi-signature Wallets**: Require multiple approvals
- **Daily Withdrawal Limits**: Configurable per user/VIP level
- **Fraud Detection**: Pattern analysis for suspicious activity
- **Cold Storage**: Majority of funds in offline wallets

## 🎯 Admin Features

### System Management

#### Service Control
```bash
# Start/stop/restart the casino
sudo systemctl start neon-casino
sudo systemctl stop neon-casino
sudo systemctl restart neon-casino

# Check status
sudo systemctl status neon-casino

# View logs
sudo journalctl -u neon-casino -f
```

#### Database Management
```bash
# Backup database
sudo /usr/local/bin/neon-casino-backup

# Monitor system
sudo /usr/local/bin/neon-casino-monitor
```

### Configuration Updates

#### Hot Reload Settings
Most configuration changes can be applied without restart:
```bash
# Update game settings
sudo systemctl reload neon-casino
```

#### Critical Updates
For major changes, restart required:
```bash
sudo systemctl restart neon-casino
```

## 📈 Performance Optimization

### Recommended Server Specs

#### Minimum (100 concurrent users)
- **CPU**: 2 cores
- **RAM**: 4GB
- **Storage**: 50GB SSD
- **Bandwidth**: 100 Mbps

#### Recommended (1000 concurrent users)
- **CPU**: 4 cores
- **RAM**: 8GB
- **Storage**: 100GB SSD
- **Bandwidth**: 1 Gbps

#### Enterprise (10,000+ concurrent users)
- **CPU**: 8+ cores
- **RAM**: 16GB+
- **Storage**: 500GB+ SSD
- **Bandwidth**: 10 Gbps
- **Load Balancer**: Multiple instances

### Scaling Considerations
- **Horizontal Scaling**: Multiple bot instances
- **Database Sharding**: Distribute users across databases
- **CDN Integration**: Static asset delivery
- **Caching Layer**: Redis for hot data

## 🔧 Troubleshooting

### Common Issues

#### Bot Not Responding
```bash
# Check service status
sudo systemctl status neon-casino

# View recent logs
sudo journalctl -u neon-casino -n 50

# Restart if needed
sudo systemctl restart neon-casino
```

#### Database Connection Issues
```bash
# Check Firebase credentials
ls -la /opt/neon-casino/neonrollfirebase-service-account.json

# Verify network connectivity
curl -I https://firebase.googleapis.com
```

#### SSL Certificate Problems
```bash
# Renew certificate
sudo certbot renew

# Check certificate status
sudo certbot certificates
```

### Performance Issues

#### High Memory Usage
```bash
# Monitor memory
htop

# Check for memory leaks
sudo journalctl -u neon-casino | grep -i memory
```

#### High CPU Usage
```bash
# Profile bot performance
sudo systemctl stop neon-casino
sudo -u neon-casino /opt/neon-casino/venv/bin/python -m cProfile bot.py
```

## 🌟 Advanced Features

### Custom Game Development
The system is designed for easy game addition. Create new games by:

1. **Adding game configuration** to `config.py`
2. **Implementing game logic** in `bot.py`
3. **Creating frontend interface** in `index.html`
4. **Adding outcome calculations** to the casino engine

### API Integration
The system supports external API integration for:
- **Live crypto prices**: Real-time exchange rates
- **Blockchain monitoring**: Automatic deposit detection
- **Analytics platforms**: Business intelligence integration
- **Payment processors**: Alternative payment methods

### White Label Solutions
The platform can be customized for different brands:
- **Custom branding**: Colors, logos, themes
- **Game variations**: Different rules and payouts
- **Currency systems**: Alternative token economies
- **Regional compliance**: Jurisdiction-specific features

## 📋 License & Support

### License
This project is proprietary software. Contact for licensing terms.

### Support
- **Documentation**: Comprehensive guides included
- **Community**: Telegram support group
- **Professional Support**: Available on request
- **Custom Development**: Enterprise solutions available

### Updates & Maintenance
- **Regular Updates**: Security and feature updates
- **Backward Compatibility**: Seamless upgrades
- **Migration Tools**: Easy version transitions
- **Professional Maintenance**: 24/7 monitoring available

---

## 🎰 Ready to Launch Your Epic Casino?

**Neon Casino** provides everything needed for a professional cryptocurrency casino operation. With its epic visual design, comprehensive game library, and enterprise-grade security, you're ready to capture the crypto gaming market.

### Quick Launch Checklist
- [ ] Configure Firebase project
- [ ] Update bot token and domain
- [ ] Run installation script
- [ ] Test all games and features
- [ ] Configure monitoring and backups
- [ ] Launch and promote to users

**🚀 Welcome to the future of crypto gaming!**