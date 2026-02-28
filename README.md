# Pyrogram Telegram Parser для OpenClaw

Простой парсер Telegram-сообщений на [Pyrogram](https://docs.pyrogram.org/), который слушает сообщения из каналов и личные сообщения аккаунта, затем сохраняет их в локальную SQLite базу данных для независимой обработки.

## 📋 Описание

Этот парсер работает как автономный источник данных и позволяет:
- Мониторить сообщения в Telegram-каналах
- Обрабатывать входящие личные сообщения (DM)
- Сохранять все сообщения в SQLite БД
- Работать без зависимости от OpenClaw Gateway
- Позволять OpenClaw читать данные напрямую из БД SQL-запросами
- Логировать все операции с настраиваемым уровнем детализации

## 🚀 Быстрый старт

### 1. Установка зависимостей

```bash
pip install -r requirements.txt
```

**Зависимости:**
- `pyrogram==2.0.106` - MTProto клиент для Telegram
- `tgcrypto` - Ускорение шифрования
- `aiosqlite>=0.19` - Асинхронная работа с SQLite
- `python-dotenv>=1.0` - Управление переменными окружения

### 2. Конфигурация

Скопируйте `.env.example` в `.env` и заполните необходимые значения:

```bash
cp .env.example .env
```

```env
# Telegram API credentials
TELEGRAM_API_ID=123456789
TELEGRAM_API_HASH=abcdef1234567890abcdef1234567890

# Имя сессии (будет создан файл parser_session.session)
TELEGRAM_SESSION_NAME=parser_session

# SQLite база данных
DB_PATH=parser.db

# Логирование
LOG_LEVEL=INFO
LOG_FILE=logs/parser.log
```

### 3. Получение Telegram API ключей

1. Перейдите на [my.telegram.org](https://my.telegram.org)
2. Авторизуйтесь с номером телефона
3. Перейдите в раздел "API development tools"
4. Создайте приложение и получите `api_id` и `api_hash`

### 4. Запуск парсера

```bash
python main.py
```

При первом запуске вас попросят авторизоваться в Telegram. Следуйте инструкциям в консоли.

После успешной авторизации парсер начнёт слушать сообщения из канаде и сохранять их в `parser.db`.

## 📁 Структура проекта

```
parser/
├── main.py                      # Точка входа
├── config.py                    # Загрузка конфигурации из .env
├── db.py                        # SQLite модуль
├── logger.py                    # Настройка логирования
├── tg_client.py                 # Pyrogram клиент и регистрация обработчиков
├── channel_registry.py          # Реестр активных каналов и состояние бота
├── handlers/
│   ├── __init__.py
│   ├── channel_handler.py       # Обработчик сообщений из каналов
│   └── private_handler.py       # Обработчик личных сообщений (DM)
├── .env.example                 # Пример переменных окружения
├── requirements.txt             # Зависимости проекта
└── README.md                    # Этот файл
```

## 🔧 Конфигурация

### Переменные окружения

| Переменная | Описание | По умолчанию | Обязательная |
|-----------|---------|--------------|-------------|
| `TELEGRAM_API_ID` | ID приложения Telegram API | - | ✅ Да |
| `TELEGRAM_API_HASH` | Hash приложения Telegram API | - | ✅ Да |
| `TELEGRAM_SESSION_NAME` | Имя сессии Pyrogram | `parser_session` | ❌ Нет |
| `DB_PATH` | Путь к SQLite БД | `parser.db` | ❌ Нет |
| `LOG_LEVEL` | Уровень логирования (DEBUG, INFO, WARNING, ERROR) | `INFO` | ❌ Нет |
| `LOG_FILE` | Путь к файлу логов | `logs/parser.log` | ❌ Нет |

### Логирование

Логирование настраивается через переменные окружения:

```env
LOG_LEVEL=DEBUG      # Максимально подробно
LOG_FILE=logs/parser.log  # Сохранять в файл
```

**Формат логов:**
```
[2025-02-28 18:00:42,123] INFO parser.main: Starting Telegram Parser for OpenClaw
[2025-02-28 18:00:42,456] DEBUG parser.db: Inserted message 1: channel message_id=12345
```

**Уровни логирования:**
- `DEBUG` - Все детали, промежуточные операции
- `INFO` - Основные события (подключения, сохранение сообщений)
- `WARNING` - Предупреждения (пропущенные сообщения, ошибки)
- `ERROR` - Ошибки (исключения, отказы операций)

## 📊 SQLite база данных

### Схема таблицы messages

```sql
CREATE TABLE messages (
    id               INTEGER PRIMARY KEY AUTOINCREMENT,
    source           TEXT NOT NULL,        -- 'channel' или 'private'
    channel_id       INTEGER,
    channel_username TEXT,
    channel_title    TEXT,
    chat_id          INTEGER,
    message_id       INTEGER NOT NULL,
    text             TEXT,
    timestamp        REAL,
    from_user_id     INTEGER,
    from_username    TEXT,
    from_first_name  TEXT,
    created_at       DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_messages_timestamp ON messages(timestamp);
CREATE INDEX idx_messages_channel ON messages(channel_username);
```

### Доступ к БД

**Просмотр сообщений из канала:**
```bash
sqlite3 parser.db "SELECT message_id, text, timestamp FROM messages WHERE channel_username = '@news' ORDER BY timestamp DESC LIMIT 10;"
```

**Подсчет сообщений:**
```bash
sqlite3 parser.db "SELECT channel_username, COUNT(*) as count FROM messages GROUP BY channel_username;"
```

**Получение последних сообщений:**
```bash
sqlite3 parser.db "SELECT * FROM messages ORDER BY created_at DESC LIMIT 5;"
```

**Экспорт в CSV:**
```bash
sqlite3 parser.db ".mode csv" "SELECT * FROM messages;" > messages.csv
```

### Python API для работы с БД

```python
from db import Database

# Инициализировать БД
db = Database("parser.db")
await db.init()

# Вставить сообщение
payload = {
    "source": "channel",
    "channel_id": 123,
    "channel_username": "@news",
    "message_id": 456,
    "text": "Hello",
    "timestamp": 1708884000.0,
    "from_user": {"id": 789, "username": "john", "first_name": "John"}
}
row_id = await db.insert_message(payload)

# Закрыть БД
await db.close()
```

## 📝 Примеры использования

### Пример 1: Запуск парсера

```bash
$ python main.py
[2025-02-28 18:00:42,123] INFO parser.main: Starting Telegram Parser for OpenClaw
[2025-02-28 18:00:42,456] INFO parser.db: Connected to database at parser.db
[2025-02-28 18:00:43,789] INFO parser.main: Starting Pyrogram client
[2025-02-28 18:00:45,000] INFO parser.main: Pyrogram client started
```

### Пример 2: Добавление канала вручную

Отредактируйте `channels.json`:

```json
{
  "channels": ["@news", "@updates"],
  "enabled": true
}
```

Парсер автоматически загружает это при старте.

### Пример 3: Чтение сообщений из Python

```python
import sqlite3

conn = sqlite3.connect("parser.db")
cursor = conn.cursor()

# Получить последние 10 сообщений
cursor.execute("""
    SELECT message_id, channel_username, text, timestamp 
    FROM messages 
    ORDER BY timestamp DESC 
    LIMIT 10
""")

for row in cursor.fetchall():
    message_id, channel, text, timestamp = row
    print(f"[{channel}] #{message_id}: {text[:50]}...")

conn.close()
```

### Пример 4: Интеграция с Flask API

```python
from flask import Flask, jsonify
import sqlite3

app = Flask(__name__)

@app.route("/api/messages/<channel>")
def get_channel_messages(channel):
    conn = sqlite3.connect("parser.db")
    conn.row_factory = sqlite3.Row
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
    
    return jsonify(messages)

if __name__ == "__main__":
    app.run(port=5000)
```

Запуск:
```bash
pip install flask
python app.py
curl http://localhost:5000/api/messages/news
```

## 🔍 Логирование и отладка

### Просмотр логов

В консоли:
```bash
python main.py
```

В файле (если LOG_FILE установлен):
```bash
tail -f logs/parser.log
```

### Уровни детализации

**DEBUG** - для разработки:
```env
LOG_LEVEL=DEBUG
```

Выведет все операции с БД:
```
[2025-02-28 18:00:42,123] DEBUG parser.db: Inserted message 1: channel message_id=12345
[2025-02-28 18:00:43,456] DEBUG parser.handler.channel: Storing channel message: {...}
```

**INFO** - для продакшена:
```env
LOG_LEVEL=INFO
```

Выведет только важные события:
```
[2025-02-28 18:00:42,123] INFO parser.main: Starting Telegram Parser for OpenClaw
[2025-02-28 18:00:42,456] INFO parser.db: Database tables initialized
[2025-02-28 18:00:43,789] INFO parser.main: Starting Pyrogram client
```

## 🐛 Решение проблем

### Ошибка: "TELEGRAM_API_ID and TELEGRAM_API_HASH are required"

**Причина:** Переменные окружения не установлены.

**Решение:** Проверьте файл `.env` и убедитесь, что заполнены `TELEGRAM_API_ID` и `TELEGRAM_API_HASH`.

```bash
cat .env | grep TELEGRAM
```

### Сообщения из канала не поступают

**Причина:**
- Канал не добавлен в реестр
- Бот отключен глобально
- Канал недоступен аккаунту

**Решение:**
1. Убедитесь, что канал добавлен в `channels.json`
2. Проверьте `"enabled": true` в `channels.json`
3. Убедитесь, что аккаунт имеет доступ к каналу
4. Проверьте логи с `LOG_LEVEL=DEBUG`

```bash
cat channels.json
LOG_LEVEL=DEBUG python main.py | grep -i "channel"
```

### БД файл не создаётся

**Причина:**
- Нет прав на запись в директорию
- Неверный путь в DB_PATH

**Решение:**
```bash
# Проверить права
ls -la parser.db

# Проверить путь в .env
grep DB_PATH .env

# Создать директорию если её нет
mkdir -p logs
```

### "Session expired" при запуске парсера

**Причина:** Файл сессии Telegram истекал.

**Решение:** Удалите файл сессии и переавторизуйтесь:

```bash
rm parser_session.session
python main.py
# Следуйте инструкциям авторизации
```

## 🔒 Безопасность

### Переменные окружения

- Никогда не коммитьте `.env` файл в git
- `.env` добавлен в `.gitignore`
- Храните все секреты в переменных окружения

### Лучшие практики

1. **Используйте отдельный аккаунт для парсера:**
   - Не используйте личный аккаунт
   - Если возможно, используйте тестовый аккаунт

2. **Логирование:** Не включайте `LOG_LEVEL=DEBUG` в продакшене

3. **БД:** Ограничьте доступ к файлу `parser.db`
   ```bash
   chmod 600 parser.db
   ```

4. **Мониторинг:** Регулярно проверяйте размер БД
   ```bash
   ls -lh parser.db
   ```

## 📚 Дополнительно

### Документация зависимостей

- [Pyrogram Documentation](https://docs.pyrogram.org/)
- [aiosqlite Documentation](https://aiosqlite.readthedocs.io/)
- [python-dotenv Documentation](https://python-dotenv.readthedocs.io/)
- [SQLite Documentation](https://www.sqlite.org/docs.html)

### Полезные команды

```bash
# Установка в режиме разработки
pip install -r requirements.txt

# Проверка синтаксиса
python -m py_compile *.py handlers/*.py

# Запуск с DEBUG логированием
LOG_LEVEL=DEBUG python main.py

# Просмотр логов в реальном времени
tail -f logs/parser.log | grep -E "INFO|ERROR"

# Проверка БД
sqlite3 parser.db "SELECT COUNT(*) as count FROM messages;"
```

## 📄 Лицензия

MIT

## 👥 Контрибьютинг

Принимаются pull requests с улучшениями и исправлениями.

## 📞 Поддержка

При возникновении проблем:
1. Проверьте логи с `LOG_LEVEL=DEBUG`
2. Убедитесь в правильности конфигурации
3. Проверьте доступность Telegram сети
4. Откройте issue с описанием проблемы и логами
