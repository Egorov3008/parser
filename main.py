import asyncio
import logging
from pyrogram import idle
from logger import setup_logging
from config import TELEGRAM_API_ID, TELEGRAM_API_HASH
from tg_client import build_client, register_handlers
from gateway_client import GatewayClient
from channel_registry import ChannelRegistry
from command_handler import handle_gateway_command

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

    # Import config after logger is set up
    import config

    # Initialize components
    registry = ChannelRegistry()
    gateway = GatewayClient(config.OPENCLAW_GATEWAY_URL, config.OPENCLAW_GATEWAY_TOKEN)
    app = None

    try:
        # Connect to OpenClaw Gateway
        await gateway.connect()

        # Build and register Pyrogram client
        app = build_client()
        register_handlers(app, gateway, registry)

        # Create task for listening to gateway commands
        async def command_callback(frame):
            await handle_gateway_command(frame, registry, gateway, app)

        listen_task = asyncio.create_task(gateway.listen(command_callback))

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
            await gateway.close()
        except Exception as e:
            logger.warning(f"Error closing gateway: {e}")
        logger.info("Shutdown complete")


if __name__ == "__main__":
    asyncio.run(main())
