#!/usr/bin/env python3
"""
Скрипт для авторизации бота в Telegram
"""

import asyncio
import sys
from pathlib import Path

# Добавляем корень проекта в path
sys.path.insert(0, str(Path(__file__).parent.parent))

from pyrogram import Client
from logger import setup_logging
import logging

setup_logging()
logger = logging.getLogger("auth")

async def main():
    """Авторизация нового бота с кодом SMS"""
    print("=" * 60)
    print("🤖 Telegram Bot Authorizer")
    print("=" * 60)
    print()
    print("📱 Введи код SMS который получил на номер +79253024139")
    print()
    
    # Создаем клиент БЕЗ phone_number для первого шага
    app = Client(
        name="parser_session",
        api_id=21314778,
        api_hash="bff27137fcbe0d9ee91034f4f61143dd",
        workdir="memory/telegram_sessions",
        device_model="Python Script",
        app_version="1.0",
        system_version="Linux"
    )
    
    try:
        # Запрашиваем код
        print("📨 Отправка запроса кода...")
        code_hash = await app.send_code("+79253024139")
        print("✅ Код отправлен!")
        print()
        print("Введи код из SMS в терминал:")
        
        # Получаем код от пользователя
        code = input(">>> ").strip()
        
        if not code:
            print("❌ Код не введен")
            return
            
        # Авторизуемся с кодом
        print()
        print("⏳ Авторизация...")
        await app.sign_in(phone="+79253024139", code=code, code_hash=code_hash.code_hash)
        
        print()
        print("=" * 60)
        print("🎉 Авторизация успешна!")
        print("=" * 60)
        print()
        
        # Проверяем
        me = await app.get_me()
        print(f"✅ Авторизован как: @{me.username} ({me.first_name})")
        print()
        
        # Сохраняем сессию
        print("💾 Сессия сохранена в memory/telegram_sessions/")
        print()
        print("Теперь можно запускать парсер:")
        print("  systemctl restart telegram-parser")
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        
    finally:
        await app.disconnect()

if __name__ == "__main__":
    asyncio.run(main())
