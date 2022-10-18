import sqlite3
from datetime import datetime


def singleton(cls):
    instances = {}

    def getinstance():
        if cls not in instances:
            instances[cls] = cls()
        return instances[cls]

    return getinstance


class DatabaseDriver(object):
    """
    Database driver for the Venmo (Full) app.
    Handles with reading and writing data with the database.
    """

    def __init__(self):
        self.conn = sqlite3.connect("venmo.db", check_same_thread=False)
        try:
            self.create_user_table()
        except Exception as e:
            pass
        self.create_transactions_table()


    def create_user_table(self):
        """
        Using SQL, creates a user table
        """
        self.conn.execute("""
        CREATE TABLE user(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        username TEXT NOT NULL,
        balance INTEGER NOT NULL
        );
        """)


    def delete_user_table(self):
        """
        Using SQL, delete a user table
        """
        self.conn.execute("DROP TABLE IF EXISTS user;")

    def get_all_users(self):
        """
        Using SQL, gets all users from the user table
        """
        cursor = self.conn.execute("SELECT * FROM user;")
        users = []

        for row in cursor:
            users.append({"id": row[0], "name": row[1], "username": row[2]})
        return users
    
    def insert_user(self, name, username, balance):
        """
        Using SQL, inserts a user into the user table
        """
        cursor = self.conn.execute("INSERT INTO user (name, username, balance) VALUES (?,?,?);", (name, username, balance))
        self.conn.commit()
        return cursor.lastrowid
    
    def get_user_by_id(self, id):
        """
        Using SQL, gets a user by its id
        """
        cursor = self.conn.execute("SELECT * FROM user WHERE id = ?;", (id,))
        for row in cursor:
            return{"id":row[0], "name": row[1], "username": row[2], "balance": row[3]}
        return None

    def delete_user_by_id(self, id):
        """
        Using SQL, deletes a user by its id
        """
        self.conn.execute("DELETE FROM user WHERE id =?;",(id,))
        self.conn.commit()

    def make_transfer(self, sender_id, receiver_id, amount):
        """
        Using SQL, updates sender's and reciever's balance with amount transfered
        """
        cursor = self.conn.execute("SELECT balance FROM user WHERE id = ?;", (sender_id,))
        sender_balance = 0
        for row in cursor:
            sender_balance = row[0] - amount
        self.conn.execute(
            """
            UPDATE user
            SET balance = ?
            WHERE id = ?;
            """,
            (sender_balance, sender_id)
        )
        self.conn.commit()
        cursor = self.conn.execute("SELECT balance FROM user WHERE id = ?;", (receiver_id,))
        receiver_balance = 0
        for row in cursor:
            receiver_balance = row[0] + amount
        self.conn.execute(
            """
            UPDATE user
            SET balance = ?
            WHERE id = ?;
            """,
            (receiver_balance, receiver_id)
        )
        self.conn.commit()

    def create_transactions_table(self):
        """
        Using SQL, creates a transactions table
        """
        self.conn.execute(
        """
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            sender_id INTEGER SECONDARY KEY NOT NULL,
            receiver_id INTEGER SECONDARY KEY NOT NULL,
            amount INTEGER NOT NULL,
            message TEXT NOT NULL,
            accepted BOOL
        );
        """)
    def delete_transactions_table(self):
        """
        Using SQL, delete a transactions table
        """
        self.conn.execute("DROP TABLE IF EXISTS transactions;")

    def insert_transaction(self, sender_id, receiver_id, amount, message, accepted):
        """
        Using SQL, inserts transaction into transactions table
        """
        cursor = self.conn.execute("INSERT INTO transactions (timestamp, sender_id, receiver_id, amount, message, accepted) VALUES (?,?,?,?,?,?);", (datetime.now(), sender_id, receiver_id, amount, message, accepted))
        self.conn.commit()
        return cursor.lastrowid

    def get_transaction_of_user(self, id):
        """
        Using SQL, returns all the transactions of a user
        """
        cursor = self.conn.execute("SELECT * FROM transactions WHERE sender_id = ? OR receiver_id = ?;", (id,id))
        transactions = []
        for row in cursor:
            transactions.append({
                "id":row[0],
                "timestamp": row[1],
                "sender_id": row[2],
                "receiver_id": row[3],
                "amount": row[4],
                "message":row[5],
                "accepted":row[6] if type(row[6]) == type(None) else bool(row[6])
            })
        return  transactions 

    def get_transaction_by_id(self, id):
        """
        Using SQL, gets a transaction by its id
        """
        cursor = self.conn.execute("SELECT * FROM transactions WHERE id = ?;", (id,))
        for row in cursor:
            return{
                "id":row[0],
                "timestamp": row[1],
                "sender_id": row[2],
                "receiver_id": row[3],
                "amount": row[4],
                "message":row[5],
                "accepted":row[6] if type(row[6]) == type(None) else bool(row[6])
                }
    
    def update_transaction(self, id, accepted):
        """
        Using SQL, updates transaction with accepted value
        """
        self.conn.execute(
            """
            UPDATE transactions
            SET timestamp = ?,
                accepted = ?
            WHERE id = ?;
            """,
            (datetime.now(), accepted, id)
        )
        self.conn.commit()

DatabaseDriver = singleton(DatabaseDriver)