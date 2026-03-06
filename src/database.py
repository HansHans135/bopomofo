"""
The database module of the bot.
"""

from datetime import date
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

            await db.execute(
                """
                CREATE TABLE IF NOT EXISTS users (
                    userid TEXT PRIMARY KEY,
                    ai_count_today INTEGER DEFAULT 0,
                    ai_count_total INTEGER DEFAULT 0,
                    last_used_date TEXT
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

    async def get_user_ai_count_today(self, userid: str) -> int:
        """
        Gets the AI usage count for today for a specific user.
        Returns 0 if the user has not used AI today.
        """
        today = str(date.today())
        async with aiosqlite.connect(self.path) as db:
            cursor = await db.execute(
                "SELECT ai_count_today, last_used_date FROM users WHERE userid = ?",
                (userid,),
            )
            result = await cursor.fetchone()
            if result is None:
                return 0
            ai_count_today, last_used_date = result
            return ai_count_today if last_used_date == today else 0

    async def get_user_ai_count_total(self, userid: str) -> int:
        """
        Gets the total AI usage count for a specific user.
        """
        async with aiosqlite.connect(self.path) as db:
            cursor = await db.execute("SELECT ai_count_total FROM users WHERE userid = ?", (userid,))
            result = await cursor.fetchone()
            return result[0] if result else 0

    async def add_user_ai_count(self, userid: str, count: int = 1) -> None:
        """
        Adds to the AI usage count for a specific user.
        Resets the daily count if the date has changed.
        """
        today = str(date.today())
        async with aiosqlite.connect(self.path) as db:
            cursor = await db.execute("SELECT last_used_date FROM users WHERE userid = ?", (userid,))
            result = await cursor.fetchone()

            if result is None:
                await db.execute(
                    "INSERT INTO users (userid, ai_count_today, ai_count_total, last_used_date) VALUES (?, ?, ?, ?)",
                    (userid, count, count, today),
                )
            elif result[0] != today:
                await db.execute(
                    "UPDATE users SET ai_count_today = ?, ai_count_total = ai_count_total + ?, last_used_date = ? WHERE userid = ?",
                    (count, count, today, userid),
                )
            else:
                await db.execute(
                    "UPDATE users SET ai_count_today = ai_count_today + ?, ai_count_total = ai_count_total + ? WHERE userid = ?",
                    (count, count, userid),
                )
            await db.commit()

    async def get_translate_count(self, original: str) -> int:
        """
        Gets the count of a specific translation from the database.
        
        :param original: The original text to look up
        :type original: str
        :return: The count of times this text has been translated, or None if not found
        :rtype: int or None
        """
        async with aiosqlite.connect(self.path) as db:
            cursor = await db.execute("SELECT count FROM translate WHERE original = ?", (original,))
            result = await cursor.fetchone()
            return result[0] if result else None
