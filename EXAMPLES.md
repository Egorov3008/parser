# Примеры использования

## 📝 Примеры с WebSocket клиентом

### Пример 1: Подключение и добавление канала

```python
import asyncio
import json
import websockets
import hmac
import hashlib
import secrets

async def example_add_channel():
    """Подключиться к парсеру и добавить канал."""

    token = "your_secret_token"

    async with websockets.connect("ws://localhost:3000") as websocket:
        # Handshake
        nonce = secrets.token_hex(16)
        signature = hmac.new(
            token.encode(),
            nonce.encode(),
            hashlib.sha256,
        ).hexdigest()

        connect_frame = {
            "type": "connect",
            "nonce": nonce,
            "signature": signature,
        }

        await websocket.send(json.dumps(connect_frame))
        response = await websocket.recv()
        print(f"Handshake response: {response}")

        # Добавить канал
        add_channel_frame = {
            "type": "req",
            "id": 1,
            "method": "channel.add",
            "params": {"username": "@news_channel"}
        }

        await websocket.send(json.dumps(add_channel_frame))
        response = await websocket.recv()
        response_data = json.loads(response)
        print(f"Add channel response: {json.dumps(response_data, indent=2)}")

asyncio.run(example_add_channel())
```

**Вывод:**
```
Handshake response: {"type": "connected", "ok": true}
Add channel response: {
  "type": "res",
  "id": 1,
  "ok": true,
  "payload": {
    "username": "@news_channel",
    "added": true
  }
}
```

### Пример 2: Слушание сообщений

```python
import asyncio
import json
import websockets

async def example_listen_messages():
    """Подключиться и слушать сообщения из парсера."""

    token = "your_secret_token"

    async with websockets.connect("ws://localhost:3000") as websocket:
        # Handshake (см. пример выше)
        # ...

        # Слушать сообщения
        async for message in websocket:
            frame = json.loads(message)

            if frame.get("type") == "req" and frame.get("method") == "message.ingest":
                print(f"Получено сообщение: {json.dumps(frame, indent=2)}")

                # Отправить подтверждение
                response = {
                    "type": "res",
                    "id": frame.get("id"),
                    "ok": True,
                    "payload": {"processed": True}
                }
                await websocket.send(json.dumps(response))

asyncio.run(example_listen_messages())
```

### Пример 3: Управление несколькими каналами

```python
import asyncio
import json
import websockets
import hmac
import hashlib
import secrets

class ParserClient:
    """Клиент для управления парсером."""

    def __init__(self, url: str, token: str):
        self.url = url
        self.token = token
        self.websocket = None
        self.request_id = 0

    async def connect(self):
        """Подключиться к парсеру."""
        self.websocket = await websockets.connect(self.url)

        # Handshake
        nonce = secrets.token_hex(16)
        signature = hmac.new(
            self.token.encode(),
            nonce.encode(),
            hashlib.sha256,
        ).hexdigest()

        await self.websocket.send(json.dumps({
            "type": "connect",
            "nonce": nonce,
            "signature": signature,
        }))

        response = await self.websocket.recv()
        response_data = json.loads(response)

        if response_data.get("type") != "connected":
            raise RuntimeError("Failed to connect")

    async def add_channel(self, username: str) -> bool:
        """Добавить канал."""
        self.request_id += 1

        await self.websocket.send(json.dumps({
            "type": "req",
            "id": self.request_id,
            "method": "channel.add",
            "params": {"username": username}
        }))

        response = json.loads(await self.websocket.recv())
        return response.get("ok", False)

    async def remove_channel(self, username: str) -> bool:
        """Удалить канал."""
        self.request_id += 1

        await self.websocket.send(json.dumps({
            "type": "req",
            "id": self.request_id,
            "method": "channel.remove",
            "params": {"username": username}
        }))

        response = json.loads(await self.websocket.recv())
        return response.get("ok", False)

    async def enable_bot(self) -> bool:
        """Включить парсер."""
        self.request_id += 1

        await self.websocket.send(json.dumps({
            "type": "req",
            "id": self.request_id,
            "method": "bot.enable",
            "params": {}
        }))

        response = json.loads(await self.websocket.recv())
        return response.get("ok", False)

    async def disable_bot(self) -> bool:
        """Отключить парсер."""
        self.request_id += 1

        await self.websocket.send(json.dumps({
            "type": "req",
            "id": self.request_id,
            "method": "bot.disable",
            "params": {}
        }))

        response = json.loads(await self.websocket.recv())
        return response.get("ok", False)

    async def close(self):
        """Закрыть соединение."""
        if self.websocket:
            await self.websocket.close()


async def example_manage_channels():
    """Управлять несколькими каналами."""

    client = ParserClient("ws://localhost:3000", "your_token")
    await client.connect()

    try:
        # Добавить каналы
        channels = ["@news", "@updates", "@alerts"]
        for channel in channels:
            success = await client.add_channel(channel)
            print(f"Добавлен {channel}: {success}")

        # Включить парсер
        await client.enable_bot()
        print("Парсер включен")

        # Слушать сообщения (в реальном приложении)
        # async for message in client.websocket:
        #     print(f"Message: {message}")

        # Отключить парсер
        await client.disable_bot()
        print("Парсер отключен")

        # Удалить каналы
        for channel in channels:
            success = await client.remove_channel(channel)
            print(f"Удален {channel}: {success}")

    finally:
        await client.close()


asyncio.run(example_manage_channels())
```

---

## 🔧 Примеры модификации парсера

### Пример 4: Добавление нового типа события

Модифицируем `handlers/channel_handler.py` для отправки дополнительных событий:

```python
# handlers/channel_handler.py
import logging

logger = logging.getLogger("parser.handler.channel")


async def handle_channel_message(client, message, gateway, registry):
    """Handle messages from Telegram channels."""
    try:
        # Check if channel is active
        if not message.chat or not message.chat.username:
            logger.debug("Skipping message with no channel username")
            return

        channel_username = message.chat.username
        if not registry.is_active(channel_username):
            logger.debug(f"Channel {channel_username} not active, skipping message")
            return

        # Extract message data
        text = message.text or message.caption or ""
        from_user = message.from_user
        user_info = {
            "id": from_user.id if from_user else None,
            "username": from_user.username if from_user else None,
            "first_name": from_user.first_name if from_user else None,
        } if from_user else None

        payload = {
            "channel_id": message.chat.id,
            "channel_username": channel_username,
            "channel_title": message.chat.title or "",
            "message_id": message.id,
            "text": text,
            "timestamp": message.date.timestamp() if message.date else None,
            "from_user": user_info,
        }

        logger.debug(f"Sending channel message: {payload}")
        await gateway.send_event("message.ingest", payload)

        # НОВЫЙ КОД: Отправлять дополнительное событие для реакций
        if message.reactions:
            reactions_payload = {
                "message_id": message.id,
                "channel_username": channel_username,
                "reactions": [
                    {
                        "emoji": reaction.emoji,
                        "count": reaction.count
                    }
                    for reaction in message.reactions
                ],
                "timestamp": message.date.timestamp() if message.date else None,
            }
            await gateway.send_event("message.reactions", reactions_payload)

    except Exception as e:
        logger.error(f"Error handling channel message: {e}")
```

### Пример 5: Фильтрование сообщений по длине

Модифицируем `handlers/channel_handler.py` для пропуска коротких сообщений:

```python
# handlers/channel_handler.py

MIN_MESSAGE_LENGTH = 10  # Минимальная длина сообщения

async def handle_channel_message(client, message, gateway, registry):
    """Handle messages from Telegram channels."""
    try:
        if not message.chat or not message.chat.username:
            logger.debug("Skipping message with no channel username")
            return

        channel_username = message.chat.username
        if not registry.is_active(channel_username):
            logger.debug(f"Channel {channel_username} not active, skipping message")
            return

        text = message.text or message.caption or ""

        # НОВЫЙ КОД: Пропустить короткие сообщения
        if len(text) < MIN_MESSAGE_LENGTH:
            logger.debug(f"Skipping short message ({len(text)} chars)")
            return

        # ... остальной код ...
```

### Пример 6: Сохранение сообщений в БД

Добавляем сохранение в SQLite:

```python
# handlers/channel_handler.py
import sqlite3
import logging

logger = logging.getLogger("parser.handler.channel")
DB_PATH = "messages.db"


def init_db():
    """Инициализировать БД."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY,
            message_id INTEGER,
            channel_username TEXT,
            text TEXT,
            timestamp REAL,
            user_id INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()


async def handle_channel_message(client, message, gateway, registry):
    """Handle messages from Telegram channels."""
    try:
        if not message.chat or not message.chat.username:
            logger.debug("Skipping message with no channel username")
            return

        channel_username = message.chat.username
        if not registry.is_active(channel_username):
            logger.debug(f"Channel {channel_username} not active, skipping message")
            return

        text = message.text or message.caption or ""
        from_user = message.from_user

        payload = {
            "channel_id": message.chat.id,
            "channel_username": channel_username,
            "channel_title": message.chat.title or "",
            "message_id": message.id,
            "text": text,
            "timestamp": message.date.timestamp() if message.date else None,
            "from_user": {
                "id": from_user.id if from_user else None,
                "username": from_user.username if from_user else None,
                "first_name": from_user.first_name if from_user else None,
            } if from_user else None,
        }

        # Сохранить в БД
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO messages (message_id, channel_username, text, timestamp, user_id)
            VALUES (?, ?, ?, ?, ?)
        """, (
            message.id,
            channel_username,
            text,
            message.date.timestamp() if message.date else None,
            from_user.id if from_user else None,
        ))
        conn.commit()
        conn.close()

        # Отправить в OpenClaw
        logger.debug(f"Sending channel message: {payload}")
        await gateway.send_event("message.ingest", payload)

    except Exception as e:
        logger.error(f"Error handling channel message: {e}")
```

### Пример 7: Добавление поддержки групп

Модифицируем `tg_client.py` для добавления поддержки групп:

```python
# tg_client.py
import logging
from pyrogram import Client, filters
from config import TELEGRAM_API_ID, TELEGRAM_API_HASH, TELEGRAM_SESSION_NAME

logger = logging.getLogger("parser.tg_client")


def build_client() -> Client:
    """Create and return a Pyrogram client."""
    app = Client(
        TELEGRAM_SESSION_NAME,
        api_id=TELEGRAM_API_ID,
        api_hash=TELEGRAM_API_HASH,
    )
    logger.info(f"Created Pyrogram client with session {TELEGRAM_SESSION_NAME}")
    return app


def register_handlers(app: Client, gateway, registry) -> None:
    """Register message handlers for channels and private messages."""
    from handlers.channel_handler import handle_channel_message
    from handlers.private_handler import handle_private_message
    from handlers.group_handler import handle_group_message

    @app.on_message(filters.channel)
    async def on_channel_message(client, message):
        await handle_channel_message(client, message, gateway, registry)

    @app.on_message(filters.private)
    async def on_private_message(client, message):
        await handle_private_message(client, message, gateway, registry)

    # НОВЫЙ КОД: Обработчик для групп
    @app.on_message(filters.group)
    async def on_group_message(client, message):
        await handle_group_message(client, message, gateway, registry)

    logger.info("Message handlers registered")
```

Создаем `handlers/group_handler.py`:

```python
# handlers/group_handler.py
import logging

logger = logging.getLogger("parser.handler.group")


async def handle_group_message(client, message, gateway, registry):
    """Handle messages from Telegram groups."""
    try:
        # Проверить, что группа в реестре
        # (требует расширения ChannelRegistry)

        text = message.text or message.caption or ""
        from_user = message.from_user

        if not from_user:
            logger.debug("Skipping group message with no from_user")
            return

        payload = {
            "group_id": message.chat.id,
            "group_title": message.chat.title or "",
            "message_id": message.id,
            "text": text,
            "timestamp": message.date.timestamp() if message.date else None,
            "from_user": {
                "id": from_user.id,
                "username": from_user.username,
                "first_name": from_user.first_name,
            },
        }

        logger.debug(f"Sending group message: {payload}")
        await gateway.send_event("message.ingest", payload)

    except Exception as e:
        logger.error(f"Error handling group message: {e}")
```

---

## 📊 Примеры отладки

### Пример 8: Скрипт для мониторинга

```python
# monitoring.py
import asyncio
import json
import websockets
import hmac
import hashlib
import secrets
from datetime import datetime


async def monitor_parser():
    """Мониторить входящие события от парсера."""

    token = "your_token"
    url = "ws://localhost:3000"

    async with websockets.connect(url) as websocket:
        # Handshake
        nonce = secrets.token_hex(16)
        signature = hmac.new(
            token.encode(),
            nonce.encode(),
            hashlib.sha256,
        ).hexdigest()

        await websocket.send(json.dumps({
            "type": "connect",
            "nonce": nonce,
            "signature": signature,
        }))

        response = await websocket.recv()
        print(f"[{datetime.now()}] Connected: {response}")

        # Мониторить события
        message_count = 0

        async for message in websocket:
            frame = json.loads(message)

            if frame.get("type") == "req" and frame.get("method") == "message.ingest":
                message_count += 1
                params = frame.get("params", {})

                print(f"[{datetime.now()}] Message #{message_count}")
                print(f"  Channel: {params.get('channel_username', 'N/A')}")
                print(f"  Text: {params.get('text', 'N/A')[:50]}...")
                print(f"  From: {params.get('from_user', {}).get('username', 'N/A')}")
                print()

asyncio.run(monitor_parser())
```

Запуск:
```bash
python monitoring.py
```

### Пример 9: Скрипт для тестирования

```bash
#!/bin/bash
# test_parser.sh

echo "Testing Telegram Parser..."

# Проверка синтаксиса
echo "1. Checking syntax..."
python -m py_compile *.py handlers/*.py && echo "✓ Syntax OK" || echo "✗ Syntax Error"

# Проверка импортов
echo "2. Checking imports..."
python -c "import config, logger, gateway_client, channel_registry, command_handler, tg_client" && echo "✓ Imports OK" || echo "✗ Import Error"

# Проверка конфигурации
echo "3. Checking .env..."
if [ -f ".env" ]; then
    echo "✓ .env exists"
    source .env
    [ -z "$TELEGRAM_API_ID" ] && echo "✗ TELEGRAM_API_ID not set" || echo "✓ TELEGRAM_API_ID set"
    [ -z "$TELEGRAM_API_HASH" ] && echo "✗ TELEGRAM_API_HASH not set" || echo "✓ TELEGRAM_API_HASH set"
    [ -z "$OPENCLAW_GATEWAY_TOKEN" ] && echo "✗ OPENCLAW_GATEWAY_TOKEN not set" || echo "✓ OPENCLAW_GATEWAY_TOKEN set"
else
    echo "✗ .env not found"
fi

# Проверка зависимостей
echo "4. Checking dependencies..."
pip list | grep -E "pyrogram|websockets|python-dotenv" && echo "✓ Dependencies OK" || echo "✗ Missing dependencies"

echo "All tests completed!"
```

---

## 🚀 Примеры интеграции

### Пример 10: Интеграция с Flask API

```python
# api.py
from flask import Flask, jsonify, request
from channel_registry import ChannelRegistry
import json

app = Flask(__name__)
registry = ChannelRegistry()


@app.route("/api/channels", methods=["GET"])
def get_channels():
    """Получить список каналов."""
    return jsonify({
        "channels": list(registry.channels),
        "enabled": registry.enabled,
        "count": len(registry.channels)
    })


@app.route("/api/channels", methods=["POST"])
def add_channel():
    """Добавить канал."""
    username = request.json.get("username")
    if not username:
        return jsonify({"error": "Missing username"}), 400

    success = registry.add(username)
    return jsonify({
        "success": success,
        "username": username,
        "message": "Channel added" if success else "Channel already exists"
    }), 200 if success else 409


@app.route("/api/channels/<username>", methods=["DELETE"])
def remove_channel(username):
    """Удалить канал."""
    success = registry.remove(username)
    return jsonify({
        "success": success,
        "username": username,
        "message": "Channel removed" if success else "Channel not found"
    }), 200 if success else 404


@app.route("/api/status", methods=["GET"])
def get_status():
    """Получить статус парсера."""
    return jsonify({
        "enabled": registry.enabled,
        "channels_count": len(registry.channels),
        "status": "running" if registry.enabled else "stopped"
    })


@app.route("/api/status", methods=["POST"])
def update_status():
    """Обновить статус парсера."""
    action = request.json.get("action")

    if action == "enable":
        registry.enable()
        return jsonify({"enabled": True})
    elif action == "disable":
        registry.disable()
        return jsonify({"enabled": False})
    else:
        return jsonify({"error": "Invalid action"}), 400


if __name__ == "__main__":
    app.run(debug=True, port=5000)
```

Запуск:
```bash
pip install flask
python api.py
```

Примеры использования:
```bash
# Получить каналы
curl http://localhost:5000/api/channels

# Добавить канал
curl -X POST http://localhost:5000/api/channels \
  -H "Content-Type: application/json" \
  -d '{"username": "@news"}'

# Удалить канал
curl -X DELETE http://localhost:5000/api/channels/@news

# Получить статус
curl http://localhost:5000/api/status

# Отключить парсер
curl -X POST http://localhost:5000/api/status \
  -H "Content-Type: application/json" \
  -d '{"action": "disable"}'
```

