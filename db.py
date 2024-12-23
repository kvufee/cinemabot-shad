import aiosqlite

DATABASE = 'movies.db'

async def init_db():
    async with aiosqlite.connect(DATABASE) as db:
        await db.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY,
                user_id INTEGER NOT NULL,
                username TEXT
            )
        ''')
        await db.execute('''
            CREATE TABLE IF NOT EXISTS queries (
                id INTEGER PRIMARY KEY,
                user_id INTEGER NOT NULL,
                query TEXT NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        await db.execute('''
            CREATE TABLE IF NOT EXISTS stats (
                id INTEGER PRIMARY KEY,
                user_id INTEGER NOT NULL,
                movie_title TEXT NOT NULL,
                count INTEGER DEFAULT 1
            )
        ''')
        await db.commit()

async def save_user(user_id, username):
    async with aiosqlite.connect(DATABASE) as db:
        await db.execute('''
            INSERT OR IGNORE INTO users (user_id, username) VALUES (?, ?)
        ''', (user_id, username))
        await db.commit()

async def save_query(user_id, username, query):
    await save_user(user_id, username)
    async with aiosqlite.connect(DATABASE) as db:
        await db.execute('''
            INSERT INTO queries (user_id, query) VALUES (?, ?)
        ''', (user_id, query))
        await db.commit()

async def get_history(user_id):
    async with aiosqlite.connect(DATABASE) as db:
        async with db.execute('''
            SELECT query, timestamp FROM queries WHERE user_id = ? ORDER BY timestamp DESC
        ''', (user_id,)) as cursor:
            rows = await cursor.fetchall()
            return [f"{row[0]} (at {row[1]})" for row in rows]

async def update_stats(user_id, movie_title):
    async with aiosqlite.connect(DATABASE) as db:
        async with db.execute('''
            SELECT count FROM stats WHERE user_id = ? AND movie_title = ?
        ''', (user_id, movie_title)) as cursor:
            row = await cursor.fetchone()
            if row:
                await db.execute('''
                    UPDATE stats SET count = count + 1 WHERE user_id = ? AND movie_title = ?
                ''', (user_id, movie_title))
            else:
                await db.execute('''
                    INSERT INTO stats (user_id, movie_title) VALUES (?, ?)
                ''', (user_id, movie_title))
            await db.commit()

async def get_stats(user_id):
    async with aiosqlite.connect(DATABASE) as db:
        async with db.execute('''
            SELECT movie_title, SUM(count) as total_count
            FROM stats
            WHERE user_id = ?
            GROUP BY movie_title
            ORDER BY total_count DESC
        ''', (user_id,)) as cursor:
            rows = await cursor.fetchall()
            return [f"{row[0]}: {row[1]} times" for row in rows]