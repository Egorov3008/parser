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
TELEGRAM_SESSION_NAME=parser_session
DB_PATH=parser.db                # SQLite база данных
LOG_LEVEL=INFO
LOG_FILE=logs/parser.log
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

После авторизации парсер начнёт сохранять сообщения в `parser.db`.

## 🎯 Проверка работы

### 1. Добавить канал для мониторинга

Отредактируй файл `channels.json`:

```json
{
  "channels": ["@durov"],
  "enabled": true
}
```

Или создай скрипт:

```python
from channel_registry import ChannelRegistry

registry = ChannelRegistry()
registry.add("@durov")
print(registry.channels)
```

Запуск:
```bash
python -c "from channel_registry import ChannelRegistry; r = ChannelRegistry(); r.add('@durov')"
```

### 2. Проверить логи парсера

В консоли парсера (main.py) должны появиться:

```
[2025-02-28 18:00:42,123] INFO parser.main: Starting Telegram Parser for OpenClaw
[2025-02-28 18:00:42,456] INFO parser.db: Database tables initialized
[2025-02-28 18:00:43,789] INFO parser.main: Starting Pyrogram client
[2025-02-28 18:00:45,000] INFO parser.main: Pyrogram client started
```

### 3. Когда в канал приходит сообщение:

```
[2025-02-28 18:05:00,123] DEBUG parser.handler.channel: Storing channel message: {...}
[2025-02-28 18:05:00,456] DEBUG parser.db: Inserted message 1: channel message_id=12345
```

### 4. Проверить БД

```bash
# Посмотреть структуру таблицы
sqlite3 parser.db ".schema messages"

# Проверить количество сообщений
sqlite3 parser.db "SELECT COUNT(*) as count FROM messages;"

# Посмотреть последние сообщения
sqlite3 parser.db "SELECT message_id, text, timestamp FROM messages LIMIT 5;"

# Посмотреть сообщения из конкретного канала
sqlite3 parser.db "SELECT * FROM messages WHERE channel_username = '@durov' ORDER BY timestamp DESC LIMIT 5;"
```

## 📊 Что должно получиться

### В консоли парсера (main.py):

```
[2025-02-28 18:00:42,123] INFO parser.main: Starting Telegram Parser for OpenClaw
[2025-02-28 18:00:42,456] INFO parser.db: Connected to database at parser.db
[2025-02-28 18:00:43,789] INFO parser.main: Starting Pyrogram client
[2025-02-28 18:00:45,000] INFO parser.main: Pyrogram client started
```

### Файлы в директории:

```
parser/
├── parser.db                    # ✓ Новый файл (SQLite БД)
├── parser_session.session       # ✓ Сессия Telegram (после авторизации)
├── channels.json                # ✓ Конфигурация каналов
├── logs/
│   └── parser.log              # ✓ Логи (если LOG_FILE установлен)
└── ...остальные файлы...
```

### В SQLite базе:

```bash
$ sqlite3 parser.db
SQLite version 3.40.0

sqlite> SELECT COUNT(*) FROM messages;
42

sqlite> SELECT * FROM messages LIMIT 1;
1|channel|123456789|@durov|Durov|NULL|...|Hello, World!|1708884000.0|987654321|durov|Pavel|2025-02-28 18:05:00
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

## ⚠️ Частые ошибки

### "TELEGRAM_API_ID and TELEGRAM_API_HASH are required"
✅ Заполни эти значения в `.env` файле

### "Session expired"
✅ Удали файл сессии и переавторизуйся:
```bash
rm parser_session.session
python main.py
```

### Сообщения не поступают в БД
✅ Проверь:
1. Является ли канал публичным (доступный по username)
2. Является ли канал добавленным в `channels.json`
3. Включен ли парсер (`"enabled": true` в `channels.json`)
4. Логи парсера с `LOG_LEVEL=DEBUG`

```bash
cat channels.json
LOG_LEVEL=DEBUG python main.py | grep -i "message\|channel"
```

### БД файл не создаётся
✅ Проверь права на запись в директорию:
```bash
touch test.db && rm test.db
```

## 📚 Дальше

- Читай [README.md](README.md) для подробного описания
- Смотри [ARCHITECTURE.md](ARCHITECTURE.md) для понимания архитектуры
- Проверь [DEVELOPMENT.md](DEVELOPMENT.md) для разработки
- Изучи [FAQ.md](FAQ.md) если что-то не работает

## ✅ Чек-лист

- [ ] Установил зависимости: `pip install -r requirements.txt`
- [ ] Получил Telegram API ключи на my.telegram.org
- [ ] Создал и заполнил `.env` файл
- [ ] Запустил парсер: `python main.py`
- [ ] Авторизовался в Telegram
- [ ] Добавил канал в `channels.json`
- [ ] Убедился, что БД файл создан: `ls -la parser.db`
- [ ] Проверил данные в БД: `sqlite3 parser.db "SELECT COUNT(*) FROM messages;"`
- [ ] Увидел сообщения в БД при отправке в канал

🎉 Готово! Парсер работает и сохраняет сообщения!

---

## 🚀 Что дальше?

### Для разработчиков:
- Прочитай [DEVELOPMENT.md](DEVELOPMENT.md)
- Посмотри примеры в [EXAMPLES.md](EXAMPLES.md)
- Модифицируй парсер для своих нужд

### Для интеграции с OpenClaw:
- Скопируй путь БД: `parser.db`
- Настрой OpenClaw для чтения из этого файла
- Используй SQL запросы для доступа к сообщениям

### Для остальных применений:
- Экспортируй данные в CSV: `sqlite3 parser.db ".mode csv" "SELECT * FROM messages;" > messages.csv`
- Создай REST API для доступа к данным
- Анализируй данные на Python

---

## 💬 Нужна помощь?

1. Проверь [FAQ.md](FAQ.md)
2. Включи DEBUG логирование: `LOG_LEVEL=DEBUG python main.py`
3. Посмотри логи: `tail -f logs/parser.log`
4. Прочитай документацию зависимостей
5. Откройте issue с логами и описанием проблемы
