# Lab2Server.py
# Project CS4032
# Cathal Geoghegan #11347076

import socket
import re
import sys

from server import TCPServer


class LockServer(TCPServer):
    LOCK_REGEX = "LOCK_FILE: \nFILENAME: [a-zA-Z0-9_./]*\n\n"
    LOCK_RESPONSE = "LOCK_RESPONE: \nFILENAME: %s\nTIME: %d\n\n"

    def __init__(self, port_use=None):
        TCPServer.__init__(self, port_use, self.handler)
        # TODO Create the DB table for file locking if doesn't exist

    def handler(self, message, con, addr):
        if re.match(self.LOCK_REGEX, message):
            self.get_lock(con, addr, message)
        else:
            return False
        return True

    def get_lock(self, con, addr, text):
        # Handler for file locking requests
        request = text.splitlines()
        full_path = request[1].split()[1]

        lock_time = self.lock_file(full_path)

        return_string = self.LOCK_RESPONSE % (full_path, lock_time)
        print return_string
        con.sendall(return_string)
        return

    def lock_file(self, path):
        # TODO Check if file locked and if not, lock it
        # TODO connect to sqlite DB, lock table and create lock entry if free
        return 0


def main():
    try:
        if len(sys.argv) > 1 and sys.argv[1].isdigit():
            port = int(sys.argv[1])
            server = LockServer(port)
        else:
            server = LockServer()
        server.listen()
    except socket.error, msg:
        print "Unable to create socket connection: " + str(msg)
        con = None


if __name__ == "__main__": main()
