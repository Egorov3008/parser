#!/usr/bin/env python3
"""Standalone script to fetch message history from a Telegram channel."""

import asyncio
import argparse
import logging
import sys

from config import TELEGRAM_API_ID, TELEGRAM_API_HASH, TELEGRAM_SESSION_NAME, DB_PATH
from db import Database
from tg_client import build_client
from logger import setup_logging


async def fetch_history(channel_username: str, limit: int = 100) -> None:
    """Fetch message history from a channel and save to database.

    Args:
        channel_username: Channel username (e.g., '@news')
        limit: Number of recent messages to fetch
    """
    logger = logging.getLogger("history")

    # Validate
    if not channel_username.startswith("@"):
        channel_username = f"@{channel_username}"

    # Initialize database
    db = Database(DB_PATH)
    await db.init()
    logger.info(f"Database ready: {DB_PATH}")

    # Initialize Pyrogram client
    app = build_client()
    logger.info("Pyrogram client created")

    try:
        # Start client
        await app.start()
        logger.info("Pyrogram client started")

        # Fetch history
        logger.info(f"Fetching up to {limit} messages from {channel_username}...")

        count = 0
        skipped = 0
        async for message in app.get_chat_history(channel_username, limit=limit):
            count += 1

            # Extract data
            text = message.text or message.caption or ""
            from_user = message.from_user

            payload = {
                "source": "channel",
                "channel_id": message.chat.id,
                "channel_username": message.chat.username,
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

            # Insert (duplicates silently ignored due to UNIQUE constraint)
            row_id = await db.insert_message(payload)
            if not row_id:
                skipped += 1

        logger.info(f"✓ Fetched: {count}, inserted: {count - skipped}, skipped (duplicates): {skipped}")

    except Exception as e:
        logger.error(f"Error during history fetch: {e}", exc_info=True)
        sys.exit(1)
    finally:
        await app.stop()
        await db.close()
        logger.info("Cleanup complete")


async def main():
    parser = argparse.ArgumentParser(
        description="Fetch message history from a Telegram channel",
        epilog="""
Examples:
  python history.py @durov              # Fetch last 100 messages
  python history.py @durov --limit 500  # Fetch last 500 messages
  python history.py durov               # (@ prefix added automatically)
        """,
    )

    parser.add_argument(
        "channel",
        help="Channel username (e.g., @news or news)",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=100,
        help="Number of recent messages to fetch (default: 100)",
    )

    args = parser.parse_args()

    # Setup logging
    setup_logging()

    # Validate credentials
    if not TELEGRAM_API_ID or not TELEGRAM_API_HASH:
        logging.error("TELEGRAM_API_ID and TELEGRAM_API_HASH are required in .env")
        sys.exit(1)

    # Fetch history
    await fetch_history(args.channel, args.limit)


if __name__ == "__main__":
    asyncio.run(main())
