import logging

logger = logging.getLogger("parser.handler.private")


async def handle_private_message(client, message, db, registry):
    """Handle private messages (DM) to the account.

    Captures all incoming DMs, including from info bots and channels.
    """
    try:
        # Check if bot is globally enabled
        if not registry.enabled:
            logger.debug("Bot disabled, skipping private message")
            return

        # Extract message data
        text = message.text or message.caption or ""
        from_user = message.from_user

        # If from_user missing (rare cases), use chat data
        if from_user:
            from_user_id = from_user.id
            from_username = from_user.username
            from_first_name = from_user.first_name
        else:
            # Fallback: use chat info
            from_user_id = None
            from_username = message.chat.username
            from_first_name = message.chat.title or "Unknown"
            logger.debug(f"Using fallback user info for chat {message.chat.id}")

        payload = {
            "source": "private",
            "chat_id": message.chat.id,
            "message_id": message.id,
            "text": text,
            "timestamp": message.date.timestamp() if message.date else None,
            "from_user": {
                "id": from_user_id,
                "username": from_username,
                "first_name": from_first_name,
            },
        }

        logger.debug(f"Storing private message: {payload}")
        await db.insert_message(payload)

    except Exception as e:
        logger.error(f"Error handling private message: {e}")
