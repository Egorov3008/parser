import logging

logger = logging.getLogger("parser.handler.channel")


async def handle_channel_message(client, message, db, registry):
    """Handle messages from Telegram channels."""
    try:
        # Check if channel is active
        if not message.chat or not message.chat.username:
            logger.debug("Skipping message with no channel username")
            return

        channel_username = message.chat.username
        if not registry.is_active(channel_username):
            logger.debug(f"Channel {channel_username} not active, skipping message")
            return

        # Extract message data
        text = message.text or message.caption or ""
        from_user = message.from_user
        user_info = {
            "id": from_user.id if from_user else None,
            "username": from_user.username if from_user else None,
            "first_name": from_user.first_name if from_user else None,
        } if from_user else None

        payload = {
            "source": "channel",
            "channel_id": message.chat.id,
            "channel_username": channel_username,
            "channel_title": message.chat.title or "",
            "message_id": message.id,
            "text": text,
            "timestamp": message.date.timestamp() if message.date else None,
            "from_user": user_info,
        }

        logger.debug(f"Storing channel message: {payload}")
        await db.insert_message(payload)

    except Exception as e:
        logger.error(f"Error handling channel message: {e}")
