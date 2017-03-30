import mysql.connector

class Database:
    def __init__(self):
        self.db = None
        self.cur = None

    def connect(self):
        self.db = mysql.connector.connect(db="telegram_fl_db", user="telegram_fl_user")
        self.cur = self.db.cursor()

    def register_user(self, user_id, username, group_id):
        self.cur.execute("INSERT IGNORE INTO groups (id) VALUES (%s)", (group_id,))
        self.cur.execute("INSERT IGNORE INTO users (id, username) VALUES (%s, %s)", (user_id, username))
        self.cur.execute("""INSERT IGNORE INTO users_in_groups (group_id, user_id)
            VALUES (%s, %s)""", (group_id, user_id))
        self.db.commit()

    def unregister_user(self, user_id, group_id):
        self.cur.execute("DELETE FROM users_in_groups WHERE user_id=%s", (user_id,))
        self.db.commit()
    
    def fetch_users(self, group_id):
        usernames = []
        
        self.cur.execute("SELECT user_id FROM users_in_groups WHERE group_id=%s", (group_id,))
        user_ids = [user_id[0] for user_id in self.cur.fetchall()]

        for user_id in user_ids:
            self.cur.execute("SELECT username FROM users WHERE id=%s", (user_id,))
            usernames.append(self.cur.fetchone()[0])

        return usernames

    def close(self):
        self.cur.close()
        self.db.close()
