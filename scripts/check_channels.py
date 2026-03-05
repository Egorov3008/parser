#!/usr/bin/env python3
"""
Скрипт для проверки каналов и добавления бота
"""

import asyncio
from pyrogram import Client
from pyrogram.enums import ChatType

# Твои каналы
CHANNELS = [
    "@kworkMarket_bot",
    "@git_developer",
    "@python2day"
]

async def check_channels():
    """Проверяет доступ к каналам"""
    app = Client(
        name="parser_check",
        api_id=21314778,
        api_hash="bff27137fcbe0d9ee91034f4f61143dd",
        workdir="memory/telegram_sessions",
        device_model="Python Script",
        app_version="1.0",
        system_version="Linux"
    )
    
    try:
        await app.connect()
        print("✅ Подключено к Telegram")
        print()
        
        for channel in CHANNELS:
            try:
                chat = await app.get_chat(channel)
                print(f"📺 {chat.title}")
                print(f"   Username: @{chat.username}")
                print(f"   Тип: {chat.type}")
                print(f"   ID: {chat.id}")
                
                # Проверяем, является ли канал публичным
                if chat.type == ChatType.CHANNEL:
                    if chat.username:
                        print("   ✅ Публичный канал")
                    else:
                        print("   ⚠️ Частный канал (нужна подписка)")
                
                # Проверяем, есть ли у бота доступ
                me = await app.get_me()
                try:
                    member = await app.get_chat_member(chat.id, me.id)
                    print(f"   🔑 Статус бота: {member.status}")
                except Exception as e:
                    print(f"   🔑 Бот не имеет доступа: {e}")
                
                print()
                
            except Exception as e:
                print(f"❌ Ошибка для {channel}")
                print(f"   {e}")
                print()
        
    except Exception as e:
        print(f"❌ Ошибка подключения: {e}")
    finally:
        await app.disconnect()

if __name__ == "__main__":
    asyncio.run(check_channels())
