import sqlite3

con = sqlite3.connect("db.sqlite3")
cur = con.cursor()

create_table_script = """
create table users(
id integer primary key,
username text,
password text
);




create table history(
id integer primary key,
user_id int, 
user_message_id int,
message text, 
role text
);

"""

cur.executescript(create_table_script)



import sqlite3

con = sqlite3.connect("db.sqlite3")
cur = con.cursor()

cur.executescript("""
DROP TABLE IF EXISTS history;
DROP TABLE IF EXISTS users;
""")

con.commit()
con.close()


