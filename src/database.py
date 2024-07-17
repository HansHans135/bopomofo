"""
The database module of the bot.
"""

from pathlib import Path

import aiosqlite


class Database:
    """
    The database class of the bot.
    """

    def __init__(self, path: str) -> None:
        self.path = path

    async def initialize(self) -> None:
        """
        Initializes the database.
        """
        Path(self.path).parent.mkdir(parents=True, exist_ok=True)
        async with aiosqlite.connect(self.path) as db:
            await db.execute(
                """
                CREATE TABLE IF NOT EXISTS info (
                    key TEXT UNIQUE,
                    value TEXT
                )
                """
            )
            await db.execute(
                """
                CREATE TABLE IF NOT EXISTS translate (
                    id INTEGER PRIMARY KEY,
                    original TEXT UNIQUE,
                    translated TEXT,
                    count INTEGER DEFAULT 1
                )
                """
            )

            await db.execute("INSERT OR IGNORE INTO info (key, value) VALUES ('translated_count', '0')")
            await db.commit()

    async def get_info(self, key: str) -> str:
        """
        Gets the value of a key from the info table.
        """
        async with aiosqlite.connect(self.path) as db:
            cursor = await db.execute("SELECT value FROM info WHERE key = ?", (key,))
            result = await cursor.fetchone()
            return result[0] if result else None

    async def add_translate_count(self, count: int = 1) -> None:
        """
        Adds 1 to the translated count.
        """
        async with aiosqlite.connect(self.path) as db:
            await db.execute(f"UPDATE info SET value = value + {count} WHERE key = 'translated_count'")
            await db.commit()

    async def insert_translate(self, original: str, translated: str) -> None:
        """
        Inserts a translation into the database.
        """
        async with aiosqlite.connect(self.path) as db:
            await db.execute(
                """
                INSERT OR IGNORE INTO translate (original, translated)
                VALUES (?, ?)
                ON CONFLICT
                DO UPDATE SET count = count + 1
                """,
                (original, translated),
            )
            await db.execute("UPDATE info SET value = value + 1 WHERE key = 'translated_count'")
            await db.commit()

    async def get_translate(self, original: str) -> str:
        """
        Gets the translated text from the database.
        """
        async with aiosqlite.connect(self.path) as db:
            cursor = await db.execute("SELECT translated FROM translate WHERE original = ?", (original,))
            result = await cursor.fetchone()
            return result[0] if result else None
