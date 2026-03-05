#!/usr/bin/env python3
"""
Скрипт для получения session_string из существующей сессии
"""

import asyncio
import base64
from pyrogram import Client
from pyrogram.types import User
from pathlib import Path

async def get_session_string():
    """Получить session_string из текущего подключения"""
    
    print("=" * 60)
    print("🔑 Получение session_string")
    print("=" * 60)
    print()
    print("Этот скрипт попытается получить session_string")
    print("из текущего подключения к Telegram.")
    print()
    
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
        await app.connect()
        print("✅ Подключено")
        print()
        
        # Получаем пользователя
        me = await app.get_me()
        print(f"Пользователь: @{me.username} ({me.first_name})")
        print()
        
        # Получаем session_string
        print("📨 Получение session_string...")
        session_string = await app.export_session_string()
        
        print()
        print("=" * 60)
        print("🎉 session_string получен!")
        print("=" * 60)
        print()
        print("Session string (сохрани его!):")
        print("-" * 60)
        print(session_string)
        print("-" * 60)
        print()
        print("Этот строку можно использовать для запуска парсера")
        print("без необходимости авторизации каждый раз.")
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        print()
        print("Возможно, сессия действительно повреждена.")
        
    finally:
        await app.disconnect()

if __name__ == "__main__":
    asyncio.run(get_session_string())
