from flask_login import UserMixin

class User(UserMixin):
    def __init__(self, user_id, username, role):
        self.id = user_id
        self.username = username
        self.role = role

def load_user(user_id):
    from app import mysql
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM Users WHERE user_id = %s", (user_id,))
    user = cursor.fetchone()
    if user:
        return User(user['user_id'], user['username'], user['role'])
    return None
