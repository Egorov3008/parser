# Быстрый старт (5 минут)

## ⚡ Минимальная конфигурация

### 1️⃣ Установка (1 мин)

```bash
# Установить зависимости
pip install -r requirements.txt
```

### 2️⃣ Получить Telegram ключи (3 мин)

1. Перейди на https://my.telegram.org
2. Авторизуйся с номером телефона
3. Нажми "API development tools"
4. Скопируй `api_id` и `api_hash`

### 3️⃣ Создать .env файл (1 мин)

```bash
cp .env.example .env
```

Отредактируй `.env`:
```env
TELEGRAM_API_ID=123456789        # Твой api_id
TELEGRAM_API_HASH=abcdef1234...  # Твой api_hash
OPENCLAW_GATEWAY_URL=ws://localhost:3000
OPENCLAW_GATEWAY_TOKEN=secret_token_here
LOG_LEVEL=INFO
```

## ▶️ Запуск

```bash
python main.py
```

### Первый запуск

При первом запуске парсер попросит авторизоваться:

```
Enter phone number: +1234567890
Enter the code that Telegram sent to you: 12345
```

После авторизации парсер подключится к OpenClaw Gateway.

## 🎯 Проверка работы

### В другом терминале отправь команду:

```bash
cat > send_command.py << 'EOF'
import asyncio
import json
import websockets
import hmac
import hashlib
import secrets

async def test():
    token = "secret_token_here"  # Из .env файла

    async with websockets.connect("ws://localhost:3000") as ws:
        # Handshake
        nonce = secrets.token_hex(16)
        sig = hmac.new(token.encode(), nonce.encode(), hashlib.sha256).hexdigest()

        await ws.send(json.dumps({
            "type": "connect",
            "nonce": nonce,
            "signature": sig
        }))

        # Подождать подтверждение
        print(await ws.recv())

        # Добавить канал
        await ws.send(json.dumps({
            "type": "req",
            "id": 1,
            "method": "channel.add",
            "params": {"username": "@durov"}
        }))

        print(await ws.recv())

asyncio.run(test())
EOF

python send_command.py
```

## 📊 Что должно получиться

### В консоли парсера (main.py):
```
[2025-02-25 20:36:42,123] INFO parser.main: Starting Telegram Parser for OpenClaw
[2025-02-25 20:36:42,456] INFO parser.gateway: Successfully connected to OpenClaw Gateway
[2025-02-25 20:36:43,789] INFO parser.registry: Added channel @durov
[2025-02-25 20:36:50,000] DEBUG parser.gateway: Sending req frame: {'type': 'req', ...}
```

### Когда кто-то напишет в канал @durov:
```
[2025-02-25 20:36:55,000] DEBUG parser.handler.channel: Sending channel message: {...}
[2025-02-25 20:36:55,100] DEBUG parser.gateway: Sending req frame: {'type': 'req', 'id': 1, 'method': 'message.ingest', ...}
```

## 🛠️ Основные команды

```bash
# Запустить с DEBUG логированием
LOG_LEVEL=DEBUG python main.py

# Просмотреть логи файла
tail -f logs/parser.log

# Остановить парсер
Ctrl+C

# Переавторизоваться (если сессия сломана)
rm parser_session.session
python main.py
```

## 📝 Основные операции через WebSocket

### Добавить канал
```json
{
  "type": "req",
  "id": 1,
  "method": "channel.add",
  "params": {"username": "@news_channel"}
}
```

### Удалить канал
```json
{
  "type": "req",
  "id": 2,
  "method": "channel.remove",
  "params": {"username": "@news_channel"}
}
```

### Включить парсер
```json
{
  "type": "req",
  "id": 3,
  "method": "bot.enable",
  "params": {}
}
```

### Отключить парсер
```json
{
  "type": "req",
  "id": 4,
  "method": "bot.disable",
  "params": {}
}
```

## ⚠️ Частые ошибки

### "TELEGRAM_API_ID and TELEGRAM_API_HASH are required"
✅ Заполни эти значения в `.env` файле

### "Failed to handshake with OpenClaw Gateway"
✅ Проверь что:
- OpenClaw запущен на `OPENCLAW_GATEWAY_URL`
- Токен совпадает в парсере и OpenClaw
- Интернет соединение работает

### "Session expired"
✅ Удали файл сессии и переавторизуйся:
```bash
rm parser_session.session
python main.py
```

### "ConnectionRefusedError"
✅ Проверь URL и порт:
```bash
curl -v ws://localhost:3000
```

## 📚 Дальше

- Читай [README.md](README.md) для подробного описания
- Смотри [EXAMPLES.md](EXAMPLES.md) для примеров кода
- Проверь [FAQ.md](FAQ.md) если что-то не работает
- Изучи [ARCHITECTURE.md](ARCHITECTURE.md) для понимания архитектуры

## ✅ Чек-лист

- [ ] Установил зависимости: `pip install -r requirements.txt`
- [ ] Получил Telegram API ключи на my.telegram.org
- [ ] Создал и заполнил `.env` файл
- [ ] Запустил парсер: `python main.py`
- [ ] Авторизовался в Telegram
- [ ] Отправил тестовую команду `channel.add`
- [ ] Увидел сообщение в логах парсера
- [ ] Отправил сообщение в канал
- [ ] Увидел событие `message.ingest` в OpenClaw

🎉 Готово! Парсер работает!

---

## 🚀 Что дальше?

### Для разработчиков:
- Прочитай [DEVELOPMENT.md](DEVELOPMENT.md)
- Добавь свои обработчики сообщений
- Интегрируй с твоей системой

### Для операционников:
- Настрой [Docker](README.md#docker-развёртывание)
- Подними сервис через [systemd](README.md#systemd-развёртывание)
- Подготовь логирование и мониторинг

### Для аналитиков:
- Смотри [примеры интеграции](EXAMPLES.md#интеграция-с-flask-api)
- Сохраняй сообщения в БД
- Анализируй данные

---

## 💬 Нужна помощь?

1. Проверь [FAQ.md](FAQ.md)
2. Включи DEBUG логирование: `LOG_LEVEL=DEBUG python main.py`
3. Посмотри логи: `tail -f logs/parser.log`
4. Прочитай документацию зависимостей
5. Откройте issue с логами и описанием проблемы
