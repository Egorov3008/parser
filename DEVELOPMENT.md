# Руководство по разработке

## 🔧 Настройка окружения разработки

### 1. Клонирование репозитория

```bash
git clone <repository-url>
cd parser
```

### 2. Создание виртуального окружения

```bash
python3 -m venv .venv
source .venv/bin/activate  # На Windows: .venv\Scripts\activate
```

### 3. Установка зависимостей

```bash
pip install -r requirements.txt
```

### 4. Подготовка .env файла

```bash
cp .env.example .env
# Заполните необходимые значения
```

## 📝 Структура кода

### Соглашения об именах

```python
# Модули
config.py              # Конфигурация
db.py                  # БД операции
logger.py              # Логирование
*_client.py           # Клиенты
*_handler.py          # Обработчики
*_registry.py         # Реестры

# Функции и методы
def build_client()    # Конструктор-функция
async def handle_*()  # Асинхронные обработчики
def is_active()       # Проверка состояния
async def init()      # Инициализация
```

### Структура класса

```python
class MyComponent:
    """Краткое описание."""

    def __init__(self, param1: str, param2: int):
        """
        Инициализация компонента.

        Args:
            param1: Описание параметра 1
            param2: Описание параметра 2
        """
        self.param1 = param1
        self.param2 = param2

    async def do_something(self) -> bool:
        """
        Выполнить что-то.

        Returns:
            True если успешно, False если нет
        """
        try:
            # Логика
            return True
        except Exception as e:
            logger.error(f"Error: {e}")
            return False
```

## 🧪 Тестирование

### Ручное тестирование

```bash
# Проверка синтаксиса
python -m py_compile *.py handlers/*.py

# Проверка импортов
python -c "import config, db, logger, channel_registry, tg_client"

# Запуск с DEBUG логированием
LOG_LEVEL=DEBUG python main.py

# Запуск с логированием в файл
LOG_FILE=test.log python main.py
```

### Тестирование конкретных компонентов

#### Тестирование Database

```python
import asyncio
from db import Database

async def test_db():
    db = Database("test.db")
    
    # Инициализация
    await db.init()
    print("✓ Database initialized")
    
    # Вставка сообщения
    payload = {
        "source": "channel",
        "channel_id": 123,
        "channel_username": "@test",
        "channel_title": "Test",
        "message_id": 456,
        "text": "Hello",
        "timestamp": 1708884000.0,
        "from_user": {
            "id": 789,
            "username": "testuser",
            "first_name": "Test"
        }
    }
    
    row_id = await db.insert_message(payload)
    print(f"✓ Message inserted: {row_id}")
    
    # Закрытие
    await db.close()
    print("✓ Database closed")

asyncio.run(test_db())
```

#### Тестирование ChannelRegistry

```python
from channel_registry import ChannelRegistry

registry = ChannelRegistry(persist_file="test_channels.json")

# Добавление канала
assert registry.add("@test") == True
assert registry.add("@test") == False  # Уже существует

# Проверка активности
assert registry.is_active("@test") == True

# Отключение бота
registry.disable()
assert registry.is_active("@test") == False
assert registry.enabled == False

# Включение бота
registry.enable()
assert registry.is_active("@test") == True

# Удаление канала
assert registry.remove("@test") == True
assert registry.is_active("@test") == False

# Очистка
import os
os.remove("test_channels.json")
os.remove("test.db")

print("✓ All tests passed!")
```

#### Тестирование Config

```python
# .env
TELEGRAM_API_ID=123456789
TELEGRAM_API_HASH=test_hash
DB_PATH=test.db
LOG_LEVEL=DEBUG

# Python
import config
assert config.TELEGRAM_API_ID == 123456789
assert config.LOG_LEVEL == "DEBUG"
assert config.DB_PATH == "test.db"
print("✓ Config tests passed!")
```

#### Тестирование Logger

```bash
LOG_LEVEL=DEBUG LOG_FILE=test.log python -c "
from logger import setup_logging
setup_logging()
import logging
logger = logging.getLogger('parser.test')
logger.info('Test message')
print('✓ Logger works')
"

# Проверить что файл и консоль логируют
cat test.log
rm test.log
```

### Интеграционное тестирование БД

```python
import asyncio
import sqlite3
from db import Database

async def test_integration():
    db = Database("integration_test.db")
    await db.init()
    
    # Вставить несколько сообщений
    for i in range(5):
        payload = {
            "source": "channel",
            "channel_id": 123,
            "channel_username": "@news",
            "message_id": 1000 + i,
            "text": f"Message {i}",
            "timestamp": 1708884000.0 + i,
            "from_user": {
                "id": 456,
                "username": "user",
                "first_name": "User"
            }
        }
        await db.insert_message(payload)
    
    await db.close()
    
    # Проверить БД
    conn = sqlite3.connect("integration_test.db")
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM messages")
    count = cursor.fetchone()[0]
    conn.close()
    
    assert count == 5, f"Expected 5 messages, got {count}"
    print("✓ Integration test passed!")
    
    # Очистка
    import os
    os.remove("integration_test.db")

asyncio.run(test_integration())
```

## 🐛 Отладка

### Включение DEBUG логирования

```bash
LOG_LEVEL=DEBUG python main.py
```

### Просмотр логов

```bash
# В реальном времени
tail -f logs/parser.log

# С фильтром
tail -f logs/parser.log | grep ERROR
tail -f logs/parser.log | grep "database\|db"
tail -f logs/parser.log | grep "message"

# Последние N строк
tail -100 logs/parser.log
```

### Интерактивная отладка

```bash
# Запуск с интерактивным интерпретатором после выхода
python -i main.py

# Перерыв выполнения (Ctrl+C), затем изучение состояния
```

### Логирование переменных

```python
import json
logger.debug(f"Message: {json.dumps(payload, indent=2)}")
logger.debug(f"Registry: channels={registry.channels}, enabled={registry.enabled}")
```

### Инспектирование БД

```bash
# Структура таблицы
sqlite3 parser.db ".schema messages"

# Статистика
sqlite3 parser.db "SELECT source, COUNT(*) FROM messages GROUP BY source;"

# Поиск по каналу
sqlite3 parser.db "SELECT * FROM messages WHERE channel_username = '@news' LIMIT 5;"

# Экспорт в CSV
sqlite3 parser.db ".mode csv" "SELECT * FROM messages;" > export.csv
```

## 🚀 Развёртывание

### Локальное развёртывание

```bash
# 1. Создать .env файл
cp .env.example .env
# Заполнить значения

# 2. Установить зависимости
pip install -r requirements.txt

# 3. Запустить парсер
python main.py

# 4. Проверить логи
tail -f logs/parser.log
```

### Развёртывание с systemd (Linux)

```bash
# 1. Создать сервис файл
sudo nano /etc/systemd/system/telegram-parser.service
```

```ini
[Unit]
Description=Telegram Parser for OpenClaw
After=network.target

[Service]
Type=simple
User=parser_user
WorkingDirectory=/opt/parser
Environment="PATH=/opt/parser/.venv/bin"
ExecStart=/opt/parser/.venv/bin/python main.py
Restart=on-failure
RestartSec=10s

[Install]
WantedBy=multi-user.target
```

```bash
# 2. Активировать сервис
sudo systemctl enable telegram-parser.service
sudo systemctl start telegram-parser.service

# 3. Проверить статус
sudo systemctl status telegram-parser.service

# 4. Просмотреть логи
sudo journalctl -u telegram-parser.service -f
```

### Docker развёртывание

```dockerfile
# Dockerfile
FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV TELEGRAM_SESSION_NAME=parser_session

CMD ["python", "main.py"]
```

```bash
# Сборка
docker build -t telegram-parser .

# Запуск
docker run --env-file .env \
  -v $(pwd)/parser.db:/app/parser.db \
  -v $(pwd)/logs:/app/logs \
  telegram-parser
```

### Docker Compose развёртывание

```yaml
# docker-compose.yml
version: '3.8'

services:
  parser:
    build: .
    container_name: telegram-parser
    environment:
      - TELEGRAM_API_ID=${TELEGRAM_API_ID}
      - TELEGRAM_API_HASH=${TELEGRAM_API_HASH}
      - TELEGRAM_SESSION_NAME=parser_session
      - DB_PATH=/app/parser.db
      - LOG_LEVEL=INFO
      - LOG_FILE=/app/logs/parser.log
    volumes:
      - ./logs:/app/logs
      - ./parser.db:/app/parser.db
      - ./parser_session.session:/app/parser_session.session
    restart: unless-stopped
```

```bash
# Запуск
docker-compose up -d

# Логи
docker-compose logs -f parser

# Остановка
docker-compose down
```

## 📦 Управление версиями

### Создание версии

```bash
# Обновить версию в коде
# Создать тег
git tag v1.1.0

# Запустить тесты
python -m py_compile *.py handlers/*.py

# Пушить изменения
git push origin main
git push origin v1.1.0
```

### Changelog формат

```markdown
## [1.1.0] - 2025-02-28

### Added
- SQLite database for message storage
- Autonomous operation without OpenClaw Gateway

### Changed
- Replaced WebSocket with local SQLite storage
- Simplified architecture

### Removed
- gateway_client.py (WebSocket)
- command_handler.py (command handling)
- websockets dependency

### Migration
- See ARCHITECTURE.md for new architecture
```

## 🔍 Статический анализ кода

```bash
# Установка инструментов
pip install flake8 pylint black isort

# Форматирование кода
black *.py handlers/*.py

# Сортировка импортов
isort *.py handlers/*.py

# Проверка стиля
flake8 *.py handlers/*.py

# Линтинг
pylint *.py handlers/*.py
```

## 🤝 Contributing

### Branching стратегия

```bash
# Создание новой feature ветки
git checkout -b feature/my-feature

# Делаем изменения, коммиты
git add .
git commit -m "Add: Implement my feature"

# Push и создание PR
git push origin feature/my-feature
# Создать Pull Request на GitHub
```

### Commit сообщения

```
Format: <Type>: <Description>

Types:
  - Add:      Добавление нового функционала
  - Fix:      Исправление ошибок
  - Update:   Обновление существующего кода
  - Refactor: Переорганизация кода
  - Docs:     Обновление документации
  - Test:     Добавление тестов
  - Chore:    Вспомогательные изменения

Examples:
  - Add: Support for message filtering
  - Fix: Database connection timeout
  - Update: Improve error messages
  - Refactor: Extract database operations
  - Docs: Update README with examples
  - Chore: Update dependencies
```

## 📖 Полезные ресурсы

- [Pyrogram Documentation](https://docs.pyrogram.org/)
- [aiosqlite Documentation](https://aiosqlite.readthedocs.io/)
- [asyncio Documentation](https://docs.python.org/3/library/asyncio.html)
- [SQLite Documentation](https://www.sqlite.org/docs.html)
- [Python Logging](https://docs.python.org/3/library/logging.html)
- [PEP 8 Style Guide](https://www.python.org/dev/peps/pep-0008/)

## 🎓 Обучение

### Рекомендуемый порядок изучения кода

1. **config.py** - начните здесь, простая загрузка переменных
2. **logger.py** - понимание логирования
3. **channel_registry.py** - простая логика хранения состояния
4. **db.py** - работа с SQLite БД ← НОВЫЙ МОДУЛЬ
5. **handlers/channel_handler.py** - обработка сообщений из каналов
6. **handlers/private_handler.py** - обработка личных сообщений
7. **tg_client.py** - Pyrogram интеграция
8. **main.py** - оркестрация всех компонентов

### Практические задачи

1. **Добавить новое поле в БД:**
   - Модифицировать SQL в `db.py`
   - Обновить payload в handlers
   - Тестировать вставку и чтение

2. **Добавить новый фильтр сообщений:**
   - Создать новый файл в `handlers/`
   - Зарегистрировать в `tg_client.py`
   - Сохранять через `db.insert_message()`

3. **Создать REST API для доступа к БД:**
   - Установить Flask
   - Создать routes для чтения из messages
   - Запустить как микросервис

4. **Добавить экспорт в CSV/JSON:**
   - Добавить функции в `db.py`
   - Создать CLI скрипт
   - Документировать использование

## 🆘 Получение помощи

- Проверьте логи с `LOG_LEVEL=DEBUG`
- Прочитайте документацию в README.md и ARCHITECTURE.md
- Ищите примеры в коде существующих компонентов
- Консультируйте документацию зависимостей
- Проверьте FAQ.md для частых вопросов
