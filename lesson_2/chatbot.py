import sys
import sqlite3
from getpass import getpass
from google.genai import Client
from dotenv import load_dotenv
from google.genai.types import UserContent, ModelContent

load_dotenv('.env')


class DuplicateUser(Exception):
    pass


class UserNotFound(Exception):
    pass


class DB:
    def __init__(self):
        self.con = sqlite3.connect("db.sqlite3")
        self.cur = self.con.cursor()

    def register(self, username, password):
        self.cur.execute("select 1 from users where username = ?;", (username,))
        is_exists = self.cur.fetchone()
        if is_exists:
            raise DuplicateUser(f"User with {username=} already exists.")

        try:
            self.cur.execute("insert into users(username, password) values (?, ?);", (username, password))
            self.con.commit()
        except Exception as e:
            self.con.rollback()
            print(f"Error: {e}")


    def login(self, username, password):
        self.cur.execute("select id from users where username=? and password=?;", (username, password))
        row = self.cur.fetchone()
        if row is None:
            raise UserNotFound(f"login or password is incorrect.")
        user_id = row[0]
        return user_id

    def load_history(self, user_id):
        self.cur.execute("select message, role from history where user_id=? order by user_message_id;", (user_id,))
        rows = self.cur.fetchall()
        formatted_history = []
        for row in rows:
            if row[1] == 'user':
                formatted_history.append(UserContent(row[0]))
            elif row[1] == 'model':
                formatted_history.append(ModelContent(row[0]))
        return formatted_history

    def save_message(self, user_id, message, role):
        self.cur.execute("select max(user_message_id) from history where user_id=?;", (user_id,))
        row = self.cur.fetchone()
        user_message_id = row[0] + 1 if row[0] is not None else 1

        self.cur.execute("insert into history(user_id, user_message_id, message, role) values (?, ?, ?, ?)", 
                         (user_id, user_message_id, message, role))
        self.con.commit()


class Agent:
    def __init__(self, user_id):
        self.user_id = user_id
        self.client = Client()
        self.db = DB()
        history = self.db.load_history(user_id=user_id)
        self.chat = self.client.chats.create(model='gemini-2.5-flash-lite', history=history)

    def ask(self, message):
        ai_message = self.chat.send_message(message).text
        for content in self.chat.get_history()[-2:]:
            self.db.save_message(self.user_id, content.parts[0].text, content.role)

        return ai_message


class Application:
    def __init__(self):
        self.db = DB()
        self.commands = {
            0: self.show_menu,
            1: self.register,
            2: self.login,
            3: sys.exit
        }
        self.menu = """Menu:
0. Show Menu
1. Register
2. Login
3. Exit
"""

    def show_menu(self):
        print(self.menu)

    def register(self, username = None):
        if username:
            print("Username:", username)
        else:
            username = input("Username: ")
        password1 = getpass("Password: ")
        password2 = getpass("Password (again): ")

        if password1 != password2:
            print("Passwords do not match.")
            self.register(username=username)

        self.db.register(username=username, password=password1)
        print("Registered")
    

    def login(self):
        username = input("Username: ")
        password = getpass("Password: ")
        user_id = self.db.login(username=username, password=password)

        agent = Agent(user_id=user_id)
        while True:
            user_message = input(f"{username}: ")
            if user_message.strip().lower() == "/bye":
                break

            ai_message = agent.ask(user_message)
            print(f"Agent: {ai_message}")



    def run(self):
        self.show_menu()

        while True:
            command_id = input("Command ID:")
            command_id = int(command_id)
            command = self.commands[command_id]
            command()

app = Application()
app.run()

