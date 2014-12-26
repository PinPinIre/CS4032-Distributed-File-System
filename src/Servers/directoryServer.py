# Lab2Server.py
# Project CS4032
# Cathal Geoghegan #11347076

import socket
import re
import sys
import os
import hashlib
import sqlite3 as db

from tcpServer import TCPServer


class DirectoryServer(TCPServer):
    GET_REGEX = "GET_SERVER: \nFILENAME: [a-zA-Z0-9_./]*\n\n"
    GET_RESPONSE = "SERVER: %s\nFILENAME: %s\n\n"
    DATABASE = "Database/directories.db"
    # TODO Add message to delete and create directories

    def __init__(self, port_use=None):
        TCPServer.__init__(self, port_use, self.handler)
        self.create_table()

    def handler(self, message, con, addr):
        if re.match(self.GET_REGEX, message):
            self.get_server(con, addr, message)
        else:
            return False
        return True

    def get_server(self, con, addr, text):
        # Handler for file upload requests
        request = text.splitlines()
        full_path = request[1].split()[1]

        path, file = os.path.split(full_path)
        name, ext = os.path.splitext(file)
        filename = hashlib.sha256(full_path).hexdigest() + ext
        host = self.find_host(path)

        if not host:
            print "Error: The directory doesn't exist"
            # TODO Return an ERROR response
            host = self.HOST

        return_string = self.GET_RESPONSE % (host, filename)
        print return_string
        con.sendall(return_string)
        return

    def find_host(self, path):
        print "Filepath is " + path
        return_host = False
        con = db.connect(self.DATABASE)
        with con:
            cur = con.cursor()
            cur.execute("SELECT Server FROM Directories WHERE Path = ?", (path,))
            server = cur.fetchone()
            if server:
                return_host = server[0]
        return return_host

    def create_dir(self, path, host):
        con = db.connect(self.DATABASE)
        with con:
            cur = con.cursor()
            cur.execute("INSERT INTO Directories (Path, Server) VALUES (?, ?)", (path, host))
        con.commit()
        con.close()

    def add_server(self, host):
        # TODO Add server to the DB
        return False

    def remove_dir(self, path):
        con = db.connect(self.DATABASE)
        with con:
            cur = con.cursor()
            cur.execute("DELETE FROM Directories WHERE Path = ?", (path,))
        con.commit()
        con.close()

    def create_table(self):
        # TODO create a table for directories
        con = db.connect(self.DATABASE)
        with con:
            cur = con.cursor()
            cur.execute("CREATE TABLE IF NOT EXISTS Directories(Id INTEGER PRIMARY KEY, Path TEXT, Server TEXT)")
            cur.execute("CREATE UNIQUE INDEX IF NOT EXISTS DIRS ON Directories(Path)")


def main():
    try:
        if len(sys.argv) > 1 and sys.argv[1].isdigit():
            port = int(sys.argv[1])
            server = DirectoryServer(port)
        else:
            server = DirectoryServer()
        server.listen()
    except socket.error, msg:
        print "Unable to create socket connection: " + str(msg)
        con = None


if __name__ == "__main__": main()
