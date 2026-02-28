import logging
import aiosqlite

logger = logging.getLogger("parser.db")


class Database:
    """SQLite database handler for storing Telegram messages."""

    def __init__(self, db_path: str):
        self.db_path = db_path
        self.conn = None
        self._callbacks: list = []

    async def init(self) -> None:
        """Initialize database and create tables if needed."""
        self.conn = await aiosqlite.connect(self.db_path)
        logger.info(f"Connected to database at {self.db_path}")

        # WAL mode: allows OpenClaw to read concurrently while parser writes
        await self.conn.execute("PRAGMA journal_mode=WAL")
        await self.conn.execute("PRAGMA synchronous=NORMAL")

        await self.conn.execute(
            """
            CREATE TABLE IF NOT EXISTS messages (
                id               INTEGER PRIMARY KEY AUTOINCREMENT,
                source           TEXT NOT NULL,
                channel_id       INTEGER,
                channel_username TEXT,
                channel_title    TEXT,
                chat_id          INTEGER,
                message_id       INTEGER NOT NULL,
                text             TEXT,
                timestamp        REAL,
                from_user_id     INTEGER,
                from_username    TEXT,
                from_first_name  TEXT,
                created_at       DATETIME DEFAULT CURRENT_TIMESTAMP
            )
            """
        )

        # Add unique constraints via separate queries (handles NULL values better)
        await self.conn.execute(
            """
            CREATE UNIQUE INDEX IF NOT EXISTS idx_channel_message
            ON messages(channel_username, message_id)
            WHERE source='channel' AND channel_username IS NOT NULL
            """
        )

        await self.conn.execute(
            """
            CREATE UNIQUE INDEX IF NOT EXISTS idx_private_message
            ON messages(chat_id, message_id)
            WHERE source='private' AND chat_id IS NOT NULL
            """
        )

        await self.conn.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_messages_timestamp ON messages(timestamp)
            """
        )

        await self.conn.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_messages_channel ON messages(channel_username)
            """
        )

        await self.conn.commit()
        logger.info("Database tables initialized")

    async def add_callback(self, fn) -> None:
        """Register an async callback invoked after each insert.

        The callback receives (row_id: int, payload: dict).
        """
        self._callbacks.append(fn)

    async def insert_message(self, payload: dict) -> int:
        """Insert a message into the database (duplicates are silently ignored).

        Args:
            payload: Dictionary with message data including 'source' field

        Returns:
            Row ID of inserted or existing message (0 if duplicate ignored)
        """
        try:
            source = payload.get("source", "")
            channel_id = payload.get("channel_id")
            channel_username = payload.get("channel_username")
            channel_title = payload.get("channel_title")
            chat_id = payload.get("chat_id")
            message_id = payload.get("message_id")
            text = payload.get("text")
            timestamp = payload.get("timestamp")

            from_user = payload.get("from_user") or {}
            from_user_id = from_user.get("id")
            from_username = from_user.get("username")
            from_first_name = from_user.get("first_name")

            cursor = await self.conn.execute(
                """
                INSERT OR IGNORE INTO messages (
                    source, channel_id, channel_username, channel_title,
                    chat_id, message_id, text, timestamp,
                    from_user_id, from_username, from_first_name
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    source,
                    channel_id,
                    channel_username,
                    channel_title,
                    chat_id,
                    message_id,
                    text,
                    timestamp,
                    from_user_id,
                    from_username,
                    from_first_name,
                ),
            )
            await self.conn.commit()
            row_id = cursor.lastrowid or 0
            if row_id:
                logger.debug(f"Inserted message {row_id}: {source} message_id={message_id}")
                for cb in self._callbacks:
                    try:
                        await cb(row_id, payload)
                    except Exception as e:
                        logger.error(f"Callback error: {e}")
            else:
                logger.debug(f"Duplicate skipped: {source} message_id={message_id}")
            return row_id
        except Exception as e:
            logger.error(f"Error inserting message: {e}")
            raise

    async def close(self) -> None:
        """Close database connection."""
        if self.conn:
            await self.conn.close()
            logger.info("Database connection closed")
