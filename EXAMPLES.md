# Примеры использования

## 📊 Примеры работы с БД

### Пример 1: Чтение сообщений из Python

```python
import sqlite3

conn = sqlite3.connect("parser.db")
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

# Получить все сообщения из канала
cursor.execute("""
    SELECT id, message_id, text, timestamp, from_username
    FROM messages
    WHERE channel_username = '@news'
    ORDER BY timestamp DESC
    LIMIT 10
""")

for row in cursor.fetchall():
    print(f"[{row['from_username']}] {row['text']}")

conn.close()
```

### Пример 2: Поиск сообщений по ключевому слову

```python
import sqlite3

conn = sqlite3.connect("parser.db")
cursor = conn.cursor()

keyword = "bitcoin"

# Поиск сообщений
cursor.execute("""
    SELECT message_id, channel_username, text, timestamp
    FROM messages
    WHERE text LIKE ? AND source = 'channel'
    ORDER BY timestamp DESC
    LIMIT 20
""", (f"%{keyword}%",))

results = cursor.fetchall()
print(f"Found {len(results)} messages with '{keyword}'")

for message_id, channel, text, timestamp in results:
    print(f"[{channel}] #{message_id}: {text[:50]}...")

conn.close()
```

### Пример 3: Анализ активности по каналам

```python
import sqlite3

conn = sqlite3.connect("parser.db")
cursor = conn.cursor()

# Статистика по каналам
cursor.execute("""
    SELECT 
        channel_username,
        COUNT(*) as message_count,
        COUNT(DISTINCT from_user_id) as unique_authors,
        MIN(timestamp) as first_message,
        MAX(timestamp) as last_message
    FROM messages
    WHERE source = 'channel'
    GROUP BY channel_username
    ORDER BY message_count DESC
""")

print("Channel Statistics:")
print("-" * 80)

for channel, count, authors, first, last in cursor.fetchall():
    print(f"{channel:30} | {count:5} messages | {authors:3} authors")

conn.close()
```

### Пример 4: Получение самых активных авторов

```python
import sqlite3

conn = sqlite3.connect("parser.db")
cursor = conn.cursor()

# Топ авторов
cursor.execute("""
    SELECT 
        from_username,
        COUNT(*) as message_count,
        COUNT(DISTINCT channel_username) as channels
    FROM messages
    WHERE from_username IS NOT NULL
    GROUP BY from_username
    ORDER BY message_count DESC
    LIMIT 20
""")

print("Top 20 Authors:")
print("-" * 60)
print(f"{'Username':<20} | {'Messages':<10} | {'Channels':<10}")
print("-" * 60)

for username, count, channels in cursor.fetchall():
    print(f"{username:<20} | {count:<10} | {channels:<10}")

conn.close()
```

### Пример 5: Экспорт сообщений в CSV

```python
import sqlite3
import csv

conn = sqlite3.connect("parser.db")
cursor = conn.cursor()

# Получить все сообщения
cursor.execute("""
    SELECT message_id, source, channel_username, text, timestamp, 
           from_username, created_at
    FROM messages
    ORDER BY created_at DESC
    LIMIT 1000
""")

# Экспортировать в CSV
with open("messages_export.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(["ID", "Source", "Channel", "Text", "Timestamp", 
                     "Author", "Created"])
    writer.writerows(cursor.fetchall())

print("✓ Exported to messages_export.csv")

conn.close()
```

### Пример 6: Интеграция с Flask API

```python
from flask import Flask, jsonify, request
import sqlite3

app = Flask(__name__)

def get_db():
    conn = sqlite3.connect("parser.db")
    conn.row_factory = sqlite3.Row
    return conn

@app.route("/api/messages")
def get_messages():
    """Получить последние сообщения."""
    limit = request.args.get("limit", 50, type=int)
    
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT id, message_id, source, channel_username, text, 
               timestamp, from_username
        FROM messages
        ORDER BY timestamp DESC
        LIMIT ?
    """, (limit,))
    
    messages = [dict(row) for row in cursor.fetchall()]
    conn.close()
    
    return jsonify(messages)

@app.route("/api/channels")
def get_channels():
    """Получить список всех каналов с статистикой."""
    
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT 
            channel_username,
            COUNT(*) as message_count,
            MAX(timestamp) as last_message_timestamp
        FROM messages
        WHERE source = 'channel'
        GROUP BY channel_username
        ORDER BY message_count DESC
    """)
    
    channels = []
    for row in cursor.fetchall():
        channels.append({
            "username": row["channel_username"],
            "message_count": row["message_count"],
            "last_message": row["last_message_timestamp"]
        })
    
    conn.close()
    return jsonify(channels)

@app.route("/api/channels/<channel>/messages")
def get_channel_messages(channel):
    """Получить сообщения из конкретного канала."""
    
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT id, message_id, text, timestamp, from_username
        FROM messages
        WHERE channel_username = ?
        ORDER BY timestamp DESC
        LIMIT 100
    """, (f"@{channel}",))
    
    messages = [dict(row) for row in cursor.fetchall()]
    conn.close()
    
    return jsonify({"channel": f"@{channel}", "messages": messages})

@app.route("/api/search")
def search_messages():
    """Поиск сообщений по ключевому слову."""
    
    keyword = request.args.get("q", "")
    if not keyword:
        return jsonify({"error": "Missing query parameter 'q'"}), 400
    
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT id, message_id, channel_username, text, timestamp
        FROM messages
        WHERE text LIKE ?
        ORDER BY timestamp DESC
        LIMIT 50
    """, (f"%{keyword}%",))
    
    results = [dict(row) for row in cursor.fetchall()]
    conn.close()
    
    return jsonify({"query": keyword, "results": results})

@app.route("/api/stats")
def get_stats():
    """Получить общую статистику."""
    
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT 
            (SELECT COUNT(*) FROM messages WHERE source = 'channel') as channel_messages,
            (SELECT COUNT(*) FROM messages WHERE source = 'private') as private_messages,
            (SELECT COUNT(DISTINCT channel_username) FROM messages) as total_channels,
            (SELECT COUNT(DISTINCT from_user_id) FROM messages) as total_authors,
            (SELECT MAX(timestamp) FROM messages) as last_message_time
    """)
    
    row = cursor.fetchone()
    stats = dict(row)
    conn.close()
    
    return jsonify(stats)

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
# Получить последние сообщения
curl http://localhost:5000/api/messages?limit=10

# Получить каналы
curl http://localhost:5000/api/channels

# Получить сообщения из канала
curl http://localhost:5000/api/channels/news/messages

# Поиск
curl "http://localhost:5000/api/search?q=bitcoin"

# Статистика
curl http://localhost:5000/api/stats
```

---

## 🔧 Примеры модификации парсера

### Пример 7: Добавление фильтра по длине сообщения

Модифицируем `handlers/channel_handler.py`:

```python
import logging

MIN_MESSAGE_LENGTH = 10  # Минимальная длина

logger = logging.getLogger("parser.handler.channel")

async def handle_channel_message(client, message, db, registry):
    """Handle messages from Telegram channels."""
    try:
        if not message.chat or not message.chat.username:
            logger.debug("Skipping message with no channel username")
            return

        channel_username = message.chat.username
        if not registry.is_active(channel_username):
            logger.debug(f"Channel {channel_username} not active, skipping")
            return

        text = message.text or message.caption or ""

        # ФИЛЬТР: Пропустить короткие сообщения
        if len(text) < MIN_MESSAGE_LENGTH:
            logger.debug(f"Skipping short message ({len(text)} chars)")
            return

        from_user = message.from_user

        payload = {
            "source": "channel",
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

        logger.debug(f"Storing channel message: {payload}")
        await db.insert_message(payload)

    except Exception as e:
        logger.error(f"Error handling channel message: {e}")
```

### Пример 8: Добавление новых полей в БД

1. Модифицируем `db.py` для добавления новой колонки:

```python
# В методе init() добавляем:
await self.conn.execute("""
    ALTER TABLE messages ADD COLUMN media_type TEXT;
""")
```

2. Обновляем `handlers/channel_handler.py`:

```python
# Определяем медиа тип
media_type = None
if message.photo:
    media_type = "photo"
elif message.video:
    media_type = "video"
elif message.document:
    media_type = "document"

payload = {
    # ... остальные поля ...
    "media_type": media_type,
}
```

3. Обновляем `db.py` метод `insert_message`:

```python
async def insert_message(self, payload: dict) -> int:
    # ... существующий код ...
    
    media_type = payload.get("media_type")
    
    cursor = await self.conn.execute("""
        INSERT INTO messages (
            source, channel_id, channel_username, channel_title,
            chat_id, message_id, text, timestamp,
            from_user_id, from_username, from_first_name, media_type
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        source, channel_id, channel_username, channel_title,
        chat_id, message_id, text, timestamp,
        from_user_id, from_username, from_first_name, media_type
    ))
```

---

## 📈 Примеры анализа данных

### Пример 9: Анализ тренда по дням

```python
import sqlite3
from datetime import datetime, timedelta

conn = sqlite3.connect("parser.db")
cursor = conn.cursor()

# Сообщения по дням за последние 30 дней
cursor.execute("""
    SELECT 
        DATE(created_at) as day,
        COUNT(*) as message_count,
        COUNT(DISTINCT channel_username) as active_channels
    FROM messages
    WHERE created_at >= datetime('now', '-30 days')
    GROUP BY DATE(created_at)
    ORDER BY day DESC
""")

print("Messages per Day (Last 30 days):")
print("-" * 50)
print(f"{'Date':<12} | {'Messages':<10} | {'Channels':<10}")
print("-" * 50)

for day, count, channels in cursor.fetchall():
    print(f"{day:<12} | {count:<10} | {channels:<10}")

conn.close()
```

### Пример 10: Отправка уведомлений при достижении порога

```python
import sqlite3
import smtplib
from email.mime.text import MIMEText

def check_and_notify(channel_username, min_messages=100):
    """Проверить количество новых сообщений и отправить уведомление."""
    
    conn = sqlite3.connect("parser.db")
    cursor = conn.cursor()
    
    # Получить количество сообщений за последний час
    cursor.execute("""
        SELECT COUNT(*) 
        FROM messages
        WHERE channel_username = ?
        AND created_at >= datetime('now', '-1 hour')
    """, (channel_username,))
    
    count = cursor.fetchone()[0]
    conn.close()
    
    if count >= min_messages:
        # Отправить уведомление
        subject = f"Alert: {count} messages in {channel_username}"
        body = f"Channel {channel_username} has received {count} messages in the last hour"
        
        # Здесь реализуете отправку (email, Slack, etc)
        print(f"✓ Alert triggered: {subject}")

# Примеры использования
check_and_notify("@news", min_messages=50)
check_and_notify("@updates", min_messages=100)
```

---

## 📋 Примеры скриптов утилит

### Пример 11: Скрипт для очистки старых сообщений

```python
# cleanup.py
import sqlite3
import argparse
from datetime import datetime, timedelta

parser = argparse.ArgumentParser(description="Clean old messages")
parser.add_argument("--days", type=int, default=30, 
                    help="Delete messages older than N days")
parser.add_argument("--db", default="parser.db",
                    help="Database path")
args = parser.parse_args()

conn = sqlite3.connect(args.db)
cursor = conn.cursor()

# Получить количество сообщений на удаление
cursor.execute("""
    SELECT COUNT(*) 
    FROM messages 
    WHERE created_at < datetime('now', ? || ' days')
""", (f"-{args.days}",))

count = cursor.fetchone()[0]

if count > 0:
    print(f"Deleting {count} messages older than {args.days} days...")
    cursor.execute("""
        DELETE FROM messages 
        WHERE created_at < datetime('now', ? || ' days')
    """, (f"-{args.days}",))
    conn.commit()
    print(f"✓ Deleted {cursor.rowcount} messages")
else:
    print("No messages to delete")

conn.close()
```

Использование:
```bash
# Удалить сообщения старше 90 дней
python cleanup.py --days 90

# Удалить сообщения старше 30 дней (по умолчанию)
python cleanup.py
```

### Пример 12: Скрипт для архивирования БД

```python
# archive.py
import sqlite3
import shutil
from datetime import datetime
import gzip

db_path = "parser.db"
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

# Создаём резервную копию
backup_path = f"parser_backup_{timestamp}.db"
shutil.copy(db_path, backup_path)
print(f"✓ Backup created: {backup_path}")

# Сжимаем резервную копию
with open(backup_path, 'rb') as f_in:
    with gzip.open(f"{backup_path}.gz", 'wb') as f_out:
        shutil.copyfileobj(f_in, f_out)
print(f"✓ Compressed: {backup_path}.gz")

# Удаляем несжатую копию
import os
os.remove(backup_path)
print(f"✓ Removed: {backup_path}")
```

Использование:
```bash
python archive.py
```

---

## 🚀 Примеры интеграции

### Пример 13: Интеграция с Discord webhook

```python
import sqlite3
import requests
import asyncio
from datetime import datetime, timedelta

DISCORD_WEBHOOK = "https://discordapp.com/api/webhooks/YOUR_WEBHOOK_ID/YOUR_WEBHOOK_TOKEN"

async def send_to_discord():
    """Отправить последние сообщения в Discord."""
    
    conn = sqlite3.connect("parser.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # Получить сообщения за последний час
    cursor.execute("""
        SELECT channel_username, text, from_username, timestamp
        FROM messages
        WHERE created_at >= datetime('now', '-1 hour')
        ORDER BY created_at DESC
        LIMIT 10
    """)
    
    messages = cursor.fetchall()
    conn.close()
    
    if not messages:
        print("No new messages")
        return
    
    # Форматируем сообщение для Discord
    embed = {
        "title": f"📊 Telegram Messages ({len(messages)})",
        "description": f"Last hour activity",
        "color": 3447003,
        "fields": []
    }
    
    for msg in messages:
        embed["fields"].append({
            "name": f"{msg['channel_username']} - {msg['from_username']}",
            "value": msg['text'][:100] + ("..." if len(msg['text']) > 100 else ""),
            "inline": False
        })
    
    data = {"embeds": [embed]}
    
    response = requests.post(DISCORD_WEBHOOK, json=data)
    if response.status_code == 204:
        print("✓ Sent to Discord")
    else:
        print(f"✗ Failed: {response.status_code}")

# Запуск
asyncio.run(send_to_discord())
```

---

## 🧪 Примеры тестирования

### Пример 14: Unit тесты

```python
# test_db.py
import asyncio
import tempfile
import os
from db import Database

async def test_database():
    # Создаём временную БД
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = os.path.join(tmpdir, "test.db")
        db = Database(db_path)
        
        # Инициализация
        await db.init()
        assert os.path.exists(db_path), "Database file not created"
        
        # Вставка
        payload = {
            "source": "channel",
            "channel_id": 123,
            "channel_username": "@test",
            "message_id": 456,
            "text": "Test message",
            "timestamp": 1708884000.0,
        }
        row_id = await db.insert_message(payload)
        assert row_id > 0, "Message not inserted"
        
        # Закрытие
        await db.close()
        
        print("✓ All database tests passed!")

asyncio.run(test_database())
```

Запуск:
```bash
python test_db.py
```
