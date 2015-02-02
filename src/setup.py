import sqlite3 as db

DATABASE = "Database/directories.db"
con = db.connect(DATABASE)
with con:
    cur = con.cursor()
    cur.execute('INSERT INTO Servers (Server, Port) VALUES ("0.0.0.0", 8006)')
    cur.execute('INSERT INTO Servers (Server, Port) VALUES ("0.0.0.0", 8009)')
    cur.execute('INSERT INTO Servers (Server, Port) VALUES ("0.0.0.0", 8010)')
    con.commit()
    cur.close()