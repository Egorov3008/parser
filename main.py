import asyncio
import logging
from pyrogram import idle
from logger import setup_logging
from config import TELEGRAM_API_ID, TELEGRAM_API_HASH, DB_PATH
from tg_client import build_client, register_handlers
from db import Database
from channel_registry import ChannelRegistry

logger = logging.getLogger("parser.main")


async def main():
    """Main entry point for the Telegram parser."""
    # Setup logging
    setup_logging()
    logger.info("Starting Telegram Parser for OpenClaw")

    # Validate Telegram credentials
    if not TELEGRAM_API_ID or not TELEGRAM_API_HASH:
        logger.error("TELEGRAM_API_ID and TELEGRAM_API_HASH are required")
        return

    # Initialize components
    registry = ChannelRegistry()
    db = Database(DB_PATH)
    app = None

    try:
        # Initialize database
        await db.init()

        # Build and register Pyrogram client
        app = build_client()
        register_handlers(app, db, registry)

        logger.info("Starting Pyrogram client")
        await app.start()
        logger.info("Pyrogram client started")

        # Keep the app running
        await idle()

    except KeyboardInterrupt:
        logger.info("Received interrupt signal")
    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
    finally:
        # Cleanup
        if app is not None:
            try:
                await app.stop()
            except Exception as e:
                logger.warning(f"Error stopping app: {e}")
        try:
            await db.close()
        except Exception as e:
            logger.warning(f"Error closing database: {e}")
        logger.info("Shutdown complete")


if __name__ == "__main__":
    asyncio.run(main())
