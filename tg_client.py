import logging
from pyrogram import Client, filters
from config import TELEGRAM_API_ID, TELEGRAM_API_HASH, TELEGRAM_SESSION_NAME

logger = logging.getLogger("parser.tg_client")


def build_client() -> Client:
    """Create and return a Pyrogram client."""
    app = Client(
        TELEGRAM_SESSION_NAME,
        api_id=TELEGRAM_API_ID,
        api_hash=TELEGRAM_API_HASH,
    )
    logger.info(f"Created Pyrogram client with session {TELEGRAM_SESSION_NAME}")
    return app


def register_handlers(app: Client, db, registry) -> None:
    """Register message handlers for channels and private messages."""
    # Import handlers here to avoid circular imports
    from handlers.channel_handler import handle_channel_message
    from handlers.private_handler import handle_private_message

    # Register channel message handler
    @app.on_message(filters.channel)
    async def on_channel_message(client, message):
        await handle_channel_message(client, message, db, registry)

    # Register private message handler
    @app.on_message(filters.private)
    async def on_private_message(client, message):
        await handle_private_message(client, message, db, registry)

    logger.info("Message handlers registered")
