import sqlite3

class Database:
    def __init__(self, db_name="moderation.db"):
        self.conn = sqlite3.connect(db_name)
        self.create_tables()

    def create_tables(self):
        with self.conn:
            # Table for tracking user warnings
            self.conn.execute('''CREATE TABLE IF NOT EXISTS warnings 
                (user_id INTEGER, guild_id INTEGER, count INTEGER, PRIMARY KEY (user_id, guild_id))''')
    
    def add_warning(self, user_id, guild_id):
        with self.conn:
            self.conn.execute('''INSERT INTO warnings (user_id, guild_id, count) 
                VALUES (?, ?, 1) ON CONFLICT(user_id, guild_id) 
                DO UPDATE SET count = count + 1''', (user_id, guild_id))
            cursor = self.conn.execute('SELECT count FROM warnings WHERE user_id = ? AND guild_id = ?', (user_id, guild_id))
            return cursor.fetchone()[0]

# Add this method to your Database class in database.py
def get_warnings(self, user_id, guild_id):
    cursor = self.conn.execute(
        'SELECT count FROM warnings WHERE user_id = ? AND guild_id = ?', 
        (user_id, guild_id)
    )
    result = cursor.fetchone()
    # If no warnings found, return 0
    return result[0] if result else 0


# Add this to your Database class in database.py
def reset_warnings(self, user_id, guild_id):
    with self.conn:
        self.conn.execute(
            'DELETE FROM warnings WHERE user_id = ? AND guild_id = ?', 
            (user_id, guild_id)
        )