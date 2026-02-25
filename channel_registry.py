import json
import logging
import os

logger = logging.getLogger("parser.registry")


class ChannelRegistry:
    """Registry for managing active channels and bot state."""

    def __init__(self, persist_file: str = "channels.json"):
        self.persist_file = persist_file
        self.enabled = True
        self.channels = set()
        self._load()

    def _load(self):
        """Load channels from persist file if it exists."""
        if os.path.exists(self.persist_file):
            try:
                with open(self.persist_file, "r") as f:
                    data = json.load(f)
                    self.channels = set(data.get("channels", []))
                    self.enabled = data.get("enabled", True)
                logger.info(f"Loaded {len(self.channels)} channels from {self.persist_file}")
            except Exception as e:
                logger.warning(f"Failed to load channels: {e}")

    def _save(self):
        """Save channels to persist file."""
        try:
            os.makedirs(os.path.dirname(self.persist_file) or ".", exist_ok=True)
            with open(self.persist_file, "w") as f:
                json.dump(
                    {
                        "channels": list(self.channels),
                        "enabled": self.enabled,
                    },
                    f,
                    indent=2,
                )
        except Exception as e:
            logger.warning(f"Failed to save channels: {e}")

    def add(self, username: str) -> bool:
        """Add a channel to the registry."""
        if username in self.channels:
            logger.debug(f"Channel {username} already in registry")
            return False
        self.channels.add(username)
        self._save()
        logger.info(f"Added channel {username}")
        return True

    def remove(self, username: str) -> bool:
        """Remove a channel from the registry."""
        if username not in self.channels:
            logger.debug(f"Channel {username} not in registry")
            return False
        self.channels.remove(username)
        self._save()
        logger.info(f"Removed channel {username}")
        return True

    def is_active(self, username: str) -> bool:
        """Check if a channel is active (enabled and in registry)."""
        return self.enabled and username in self.channels

    def enable(self) -> bool:
        """Enable the bot globally."""
        if self.enabled:
            logger.debug("Bot already enabled")
            return False
        self.enabled = True
        self._save()
        logger.info("Bot enabled")
        return True

    def disable(self) -> bool:
        """Disable the bot globally."""
        if not self.enabled:
            logger.debug("Bot already disabled")
            return False
        self.enabled = False
        self._save()
        logger.info("Bot disabled")
        return True
