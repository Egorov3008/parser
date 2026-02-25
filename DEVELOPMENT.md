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
pip install -e .  # Если есть setup.py
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
logger.py              # Логирование
*_client.py           # Клиенты (gateway_client.py)
*_handler.py          # Обработчики (channel_handler.py)
*_registry.py         # Реестры (channel_registry.py)

# Функции и методы
def build_client()    # Конструктор-функция
async def handle_*()  # Асинхронные обработчики
def is_active()       # Проверка состояния
def setup_*()         # Инициализация
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
python -c "import config, logger, gateway_client, channel_registry, command_handler, tg_client, main"

# Запуск с DEBUG логированием
LOG_LEVEL=DEBUG python main.py

# Запуск с логированием в файл
LOG_FILE=test.log python main.py
```

### Тестирование конкретных компонентов

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
assert registry.is_active("@test") == False  # Бот отключен
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
```

#### Тестирование Config

```python
# .env
TELEGRAM_API_ID=123456789
TELEGRAM_API_HASH=test_hash
LOG_LEVEL=DEBUG

# Python
import config
assert config.TELEGRAM_API_ID == 123456789
assert config.LOG_LEVEL == "DEBUG"
```

#### Тестирование Logger

```bash
LOG_LEVEL=DEBUG LOG_FILE=test.log python -c "
from logger import setup_logging
setup_logging()
import logging
logger = logging.getLogger('parser.test')
logger.info('Test message')
"

# Проверить что файл и консоль логируют
cat test.log
rm test.log
```

### Симуляция WebSocket сервера

```bash
# Установка инструмента для WebSocket
pip install websockets

# Создание простого сервера для тестирования
cat > test_gateway.py << 'EOF'
import asyncio
import json
import websockets

async def handler(websocket, path):
    try:
        # Получить connect фрейм
        msg = await websocket.recv()
        connect_frame = json.loads(msg)
        print(f"Received: {connect_frame}")

        # Отправить подтверждение
        await websocket.send(json.dumps({
            "type": "connected",
            "ok": True
        }))

        # Слушать входящие фреймы
        async for message in websocket:
            frame = json.loads(message)
            print(f"Received: {frame}")

            # Отправить тестовую команду
            if frame.get("type") == "req":
                await websocket.send(json.dumps({
                    "type": "res",
                    "id": frame.get("id"),
                    "ok": True,
                    "payload": {"test": "ok"}
                }))
    except Exception as e:
        print(f"Error: {e}")

async def main():
    async with websockets.serve(handler, "localhost", 3000):
        print("WebSocket server started on ws://localhost:3000")
        await asyncio.Future()

if __name__ == "__main__":
    asyncio.run(main())
EOF

# Запуск тестового сервера
python test_gateway.py

# В другом терминале запустить парсер
python main.py
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
tail -f logs/parser.log | grep "gateway"
tail -f logs/parser.log | grep "command"

# Последние N строк
tail -100 logs/parser.log
```

### Интерактивная отладка

```bash
# Запуск с интерактивным интерпретатором после выхода
python -i main.py

# Перерыв выполнения (Ctrl+C), затем изучение состояния
```

### Добавление точек останова

```python
# В коде
import pdb; pdb.set_trace()

# Или через Python debugger
python -m pdb main.py
```

### Логирование переменных

```python
import json
logger.debug(f"Frame: {json.dumps(frame, indent=2)}")
logger.debug(f"Registry state: channels={registry.channels}, enabled={registry.enabled}")
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
  -v $(pwd)/logs:/app/logs \
  -v $(pwd)/parser_session.session:/app/parser_session.session \
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
      - OPENCLAW_GATEWAY_URL=ws://gateway:3000
      - OPENCLAW_GATEWAY_TOKEN=${OPENCLAW_GATEWAY_TOKEN}
      - LOG_LEVEL=INFO
      - LOG_FILE=/app/logs/parser.log
    volumes:
      - ./logs:/app/logs
      - ./parser_session.session:/app/parser_session.session
    networks:
      - openclaw
    restart: unless-stopped

networks:
  openclaw:
    external: true
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
git tag v1.0.0

# Запустить тесты
python -m py_compile *.py handlers/*.py

# Пушить изменения
git push origin main
git push origin v1.0.0
```

### Changelog формат

```markdown
## [1.0.0] - 2025-02-25

### Added
- Initial release with channel monitoring
- WebSocket communication with OpenClaw Gateway
- Dynamic channel management through commands

### Changed
- (nothing)

### Fixed
- (nothing)

### Deprecated
- (nothing)

### Removed
- (nothing)

### Security
- HMAC-SHA256 authentication for WebSocket
```

## 🔍 Статический анализ кода

```bash
# Установка инструментов
pip install flake8 pylint mypy black isort

# Форматирование кода
black *.py handlers/*.py

# Сортировка импортов
isort *.py handlers/*.py

# Проверка стиля
flake8 *.py handlers/*.py

# Проверка типов
mypy *.py handlers/*.py

# Линтинг
pylint *.py handlers/*.py
```

## 📚 Документирование

### Стиль документации

```python
def my_function(param1: str, param2: int = 10) -> bool:
    """
    Короткое описание функции.

    Более подробное описание логики функции и её поведения
    может занимать несколько строк.

    Args:
        param1: Описание параметра 1
        param2: Описание параметра 2, по умолчанию 10

    Returns:
        True если успешно, False если ошибка

    Raises:
        ValueError: Если param1 пуст
        TypeError: Если param2 не integer

    Example:
        >>> my_function("test")
        True
        >>> my_function("", 5)
        ValueError: param1 cannot be empty
    """
    pass
```

### Генерация документации

```bash
# Установка Sphinx
pip install sphinx

# Инициализация документации
sphinx-quickstart docs

# Сборка HTML
cd docs && make html
```

## 🔐 Безопасность разработки

### Проверка секретов в коде

```bash
# Установка
pip install detect-secrets

# Сканирование
detect-secrets scan

# Добавление исключений (если есть false positives)
detect-secrets scan --all-files --baseline .secrets.baseline
```

### Pre-commit hooks

```bash
# Установка
pip install pre-commit

# Конфигурация в .pre-commit-config.yaml
cat > .pre-commit-config.yaml << 'EOF'
repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.4.0
    hooks:
      - id: check-yaml
      - id: end-of-file-fixer
      - id: trailing-whitespace
      - id: detect-private-key

  - repo: https://github.com/psf/black
    rev: 23.1.0
    hooks:
      - id: black

  - repo: https://github.com/PyCQA/flake8
    rev: 6.0.0
    hooks:
      - id: flake8
EOF

# Установка hooks
pre-commit install

# Запуск вручную
pre-commit run --all-files
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
  - Refactor: Переорганизация кода без изменения функционала
  - Docs:     Обновление документации
  - Test:     Добавление или обновление тестов
  - Chore:    Вспомогательные изменения (зависимости и т.д.)

Examples:
  - Add: Support for message reactions
  - Fix: WebSocket reconnection on disconnect
  - Update: Improve error messages for invalid commands
  - Refactor: Extract command validation to separate module
  - Docs: Add example configuration
  - Chore: Update dependencies
```

## 📖 Полезные ресурсы

- [Pyrogram Documentation](https://docs.pyrogram.org/)
- [asyncio Documentation](https://docs.python.org/3/library/asyncio.html)
- [websockets Documentation](https://websockets.readthedocs.io/)
- [Python Logging](https://docs.python.org/3/library/logging.html)
- [PEP 8 Style Guide](https://www.python.org/dev/peps/pep-0008/)
- [Type Hints](https://docs.python.org/3/library/typing.html)

## 🎓 Обучение

### Рекомендуемый порядок изучения кода

1. **config.py** - начните здесь, простая загрузка переменных
2. **logger.py** - понимание логирования
3. **channel_registry.py** - простая логика хранения состояния
4. **gateway_client.py** - WebSocket коммуникация
5. **command_handler.py** - обработка команд
6. **handlers/channel_handler.py** - обработка сообщений из каналов
7. **handlers/private_handler.py** - обработка личных сообщений
8. **tg_client.py** - Pyrogram интеграция
9. **main.py** - оркестрация всех компонентов

### Практические задачи

1. **Добавить новую команду:**
   - Добавить обработку в `command_handler.py`
   - Добавить соответствующий метод в `ChannelRegistry`
   - Протестировать с WebSocket клиентом

2. **Добавить новый фильтр сообщений:**
   - Создать новый файл в `handlers/`
   - Зарегистрировать в `tg_client.py`
   - Добавить логирование

3. **Улучшить логирование:**
   - Добавить новые уровни логирования
   - Структурировать логи в JSON формат
   - Интегрировать с системой мониторинга

## 🆘 Получение помощи

- Проверьте логи с `LOG_LEVEL=DEBUG`
- Прочитайте документацию в `README.md` и `ARCHITECTURE.md`
- Ищите примеры в коде существующих обработчиков
- Консультируйте документацию зависимостей
