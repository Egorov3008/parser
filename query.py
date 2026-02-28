#!/usr/bin/env python3
"""CLI tool to query messages from parser.db"""

import sqlite3
import argparse
from pathlib import Path
from typing import Optional


def query_messages(
    db_path: str,
    channel: Optional[str] = None,
    source: Optional[str] = None,
    search: Optional[str] = None,
    since: Optional[str] = None,
    limit: int = 20,
) -> None:
    """Query messages from the database.

    Args:
        db_path: Path to SQLite database
        channel: Filter by channel username (e.g., '@news')
        source: Filter by source ('channel' or 'private')
        search: Search text
        since: Date filter (YYYY-MM-DD)
        limit: Max number of results
    """
    if not Path(db_path).exists():
        print(f"❌ Database not found: {db_path}")
        return

    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # Build query
    where_clauses = []
    params = []

    if source:
        where_clauses.append("source = ?")
        params.append(source)

    if channel:
        where_clauses.append("channel_username = ?")
        params.append(channel)

    if search:
        where_clauses.append("text LIKE ?")
        params.append(f"%{search}%")

    if since:
        where_clauses.append("DATE(created_at) >= ?")
        params.append(since)

    where_clause = " AND ".join(where_clauses) if where_clauses else "1=1"
    sql = f"""
        SELECT id, source, channel_username, chat_id, message_id,
               text, timestamp, from_username, created_at
        FROM messages
        WHERE {where_clause}
        ORDER BY created_at DESC
        LIMIT ?
    """
    params.append(limit)

    cursor.execute(sql, params)
    rows = cursor.fetchall()

    if not rows:
        print("No messages found")
        conn.close()
        return

    # Display results
    print(f"\n{'ID':<6} | {'Source':<10} | {'Channel/From':<20} | {'Text':<50} | {'Time':<19}")
    print("-" * 130)

    for row in rows:
        source_str = row["source"]
        channel_or_user = row["channel_username"] or row["from_username"] or "?"
        text_preview = (row["text"] or "")[:45] + ("..." if len(row["text"] or "") > 45 else "")
        time_str = row["created_at"][:19] if row["created_at"] else "?"

        print(
            f"{row['id']:<6} | {source_str:<10} | {channel_or_user:<20} | {text_preview:<50} | {time_str:<19}"
        )

    print(f"\n✓ Total: {len(rows)} messages")
    conn.close()


def main():
    parser = argparse.ArgumentParser(
        description="Query messages from parser.db",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python query.py                          # Last 20 messages
  python query.py --channel @news          # From @news channel
  python query.py --source private         # Private messages only
  python query.py --search bitcoin         # Text search
  python query.py --since 2025-02-01       # Since date
  python query.py --limit 50               # Custom limit
        """,
    )

    parser.add_argument(
        "--db",
        default="parser.db",
        help="Path to database (default: parser.db)",
    )
    parser.add_argument(
        "--channel",
        help="Filter by channel (e.g., @news)",
    )
    parser.add_argument(
        "--source",
        choices=["channel", "private"],
        help="Filter by source type",
    )
    parser.add_argument(
        "--search",
        help="Search text",
    )
    parser.add_argument(
        "--since",
        help="Date filter (YYYY-MM-DD)",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=20,
        help="Max results (default: 20)",
    )

    args = parser.parse_args()

    query_messages(
        db_path=args.db,
        channel=args.channel,
        source=args.source,
        search=args.search,
        since=args.since,
        limit=args.limit,
    )


if __name__ == "__main__":
    main()
