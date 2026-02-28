import logging

logger = logging.getLogger("parser.handler.private")


async def handle_private_message(client, message, db, registry):
    """Handle private messages (DM) to the account."""
    try:
        # Check if bot is globally enabled
        if not registry.enabled:
            logger.debug("Bot disabled, skipping private message")
            return

        # Extract message data
        text = message.text or message.caption or ""
        from_user = message.from_user

        if not from_user:
            logger.debug("Skipping private message with no from_user")
            return

        payload = {
            "source": "private",
            "chat_id": message.chat.id,
            "message_id": message.id,
            "text": text,
            "timestamp": message.date.timestamp() if message.date else None,
            "from_user": {
                "id": from_user.id,
                "username": from_user.username,
                "first_name": from_user.first_name,
            },
        }

        logger.debug(f"Storing private message: {payload}")
        await db.insert_message(payload)

    except Exception as e:
        logger.error(f"Error handling private message: {e}")
