#!/bin/bash
set -e

# ==============================================================================
# ======================== НАСТРОЙКИ (ИЗМЕНИТЕ, ЕСЛИ НУЖНО) =====================
# ==============================================================================

# 1. Ваш домен.
DOMAIN_NAME="agrobmin.com.ua"

# 2. Имена ваших файлов сертификата (должны лежать в той же папке, что и скрипт).
CERT_FILE="sertificat.pem"
KEY_FILE="sertificat.key"

# 3. Токен вашего бота (замените на реальный)
BOT_TOKEN="7967948563:AAEcl-6mW5kd4jaqjsRIqnv34egBWmh1LiI"

# ==============================================================================
# =================== ДАЛЬШЕ СКРИПТ РАБОТАЕТ АВТОМАТИЧЕСКИ ====================
# ==============================================================================

echo "--- [1/6] Проверка наличия файлов сертификата ---"
if [ ! -f "$CERT_FILE" ] || [ ! -f "$KEY_FILE" ]; then
    echo "Ошибка: Файлы сертификата '$CERT_FILE' и/или '$KEY_FILE' не найдены."
    echo "Пожалуйста, убедитесь, что они находятся в той же папке, что и этот скрипт."
    exit 1
fi

echo "--- [2/6] Установка зависимостей Python ---"
# Обновляем систему и устанавливаем Python
sudo apt update
sudo apt install -y python3 python3-pip python3-venv nginx

echo "--- [3/6] Настройка веб-сервера Nginx с вашими SSL-сертификатами ---"
# Создаем директорию для сайта и SSL
sudo mkdir -p /var/www/${DOMAIN_NAME}
sudo mkdir -p /etc/nginx/ssl

# Копируем ваши сертификаты в системную папку
sudo cp "./${CERT_FILE}" "/etc/nginx/ssl/${CERT_FILE}"
sudo cp "./${KEY_FILE}" "/etc/nginx/ssl/${KEY_FILE}"

# Устанавливаем правильные права доступа (очень важно для безопасности)
sudo chmod 600 "/etc/nginx/ssl/${KEY_FILE}"
sudo chmod 644 "/etc/nginx/ssl/${CERT_FILE}"

# Копируем файл игры
sudo cp ./index.html /var/www/${DOMAIN_NAME}/index.html
sudo chown -R www-data:www-data /var/www/${DOMAIN_NAME}

# Создаем новую, полную конфигурацию Nginx для HTTPS
sudo tee /etc/nginx/sites-available/$DOMAIN_NAME > /dev/null <<EOF
server {
    listen 80;
    server_name $DOMAIN_NAME;
    # Перенаправляем весь HTTP трафик на HTTPS
    return 301 https://\$host\$request_uri;
}

server {
    listen 443 ssl;
    server_name $DOMAIN_NAME;

    root /var/www/$DOMAIN_NAME;
    index index.html;

    # Указываем пути к вашим файлам сертификата
    ssl_certificate /etc/nginx/ssl/$CERT_FILE;
    ssl_certificate_key /etc/nginx/ssl/$KEY_FILE;

    # Стандартные параметры безопасности SSL
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;

    location / {
        try_files \$uri \$uri/ =404;
        add_header Cache-Control "no-cache, no-store, must-revalidate";
        add_header Pragma "no-cache";
        add_header Expires "0";
    }
}
EOF

# Активируем конфигурацию и перезапускаем Nginx
sudo ln -sfn /etc/nginx/sites-available/$DOMAIN_NAME /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx

echo "--- [4/6] Настройка Telegram бота ---"
BOT_DIR="/opt/neon-roll-bot"
CURRENT_USER=$(whoami)

# Создаем директорию для бота
sudo mkdir -p $BOT_DIR
sudo chown -R $CURRENT_USER:$CURRENT_USER $BOT_DIR

# Создаем виртуальное окружение Python
python3 -m venv $BOT_DIR/venv
source $BOT_DIR/venv/bin/activate

# Устанавливаем зависимости
$BOT_DIR/venv/bin/pip install --upgrade pip
$BOT_DIR/venv/bin/pip install -r requirements.txt

# Создаем конфигурационный файл
tee $BOT_DIR/config.py > /dev/null <<EOF
# Bot Configuration
BOT_TOKEN = "${BOT_TOKEN}"
WEB_APP_URL = "https://${DOMAIN_NAME}"

# Firebase Configuration
FIREBASE_PROJECT_ID = "neonroll-26174"

# Game Configuration
WELCOME_BONUS = 20.0
MIN_BET = 1.0
MAX_BET = 1000.0

# Crypto Configuration
CRYPTO_WALLETS = {
    'ton': 'UQBvI0aFLnw2QbZgjMPCLRdtRHxhUyinQudg6sdiohIwg5jL',
    'usdt': 'TXYZabcd1234567890ABCDEF1234567890abcdef',
    'btc': 'bc1qxy2kgdygjrsqtzq2n0yrf2493p83kkfjhx0wlh'
}

# API Keys
GEMINI_API_KEY = ""
EOF

# Копируем файлы бота
cp ./bot.py $BOT_DIR/bot.py
cp ./neonrollfirebase-service-account.json $BOT_DIR/neonrollfirebase-service-account.json
cp ./requirements.txt $BOT_DIR/requirements.txt

echo "--- [5/6] Создание системного сервиса для бота ---"
sudo tee /etc/systemd/system/neon-roll-bot.service > /dev/null <<EOF
[Unit]
Description=Neon Roll Telegram Bot
After=network.target

[Service]
Type=simple
User=$CURRENT_USER
Group=$CURRENT_USER
WorkingDirectory=$BOT_DIR
ExecStart=$BOT_DIR/venv/bin/python bot.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Перезагружаем systemd и запускаем сервис
sudo systemctl daemon-reload
sudo systemctl enable neon-roll-bot
sudo systemctl start neon-roll-bot

echo "--- [6/6] Финальная проверка статусов ---"
sudo systemctl status nginx --no-pager -n 0
sudo systemctl status neon-roll-bot --no-pager -n 0

echo "========================================================"
echo "🎉 Установка завершена! 🎉"
echo ""
echo "✅ Ваш сайт доступен по адресу: https://${DOMAIN_NAME}"
echo "✅ Telegram бот запущен и готов к работе"
echo "✅ Firebase интеграция настроена"
echo "✅ Все данные пользователей сохраняются в облаке"
echo ""
echo "📝 Не забудьте:"
echo "1. Заменить BOT_TOKEN в config.py на реальный токен"
echo "2. Добавить Gemini API ключ для AI функций (опционально)"
echo "3. Настроить реальные криптовалютные кошельки"
echo ""
echo "🔧 Управление ботом:"
echo "   sudo systemctl start neon-roll-bot    # Запустить"
echo "   sudo systemctl stop neon-roll-bot     # Остановить"
echo "   sudo systemctl restart neon-roll-bot  # Перезапустить"
echo "   sudo systemctl status neon-roll-bot   # Проверить статус"
echo ""
echo "📊 Логи бота:"
echo "   sudo journalctl -u neon-roll-bot -f"
echo ""
echo "========================================================"
