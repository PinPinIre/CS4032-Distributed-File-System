# Lab2Server.py
# Project CS4032
# Cathal Geoghegan #11347076

import socket
import re
import sys
import os
import hashlib

from tcpServer import TCPServer


class DirectoryServer(TCPServer):
    GET_REGEX = "GET_SERVER: \nFILENAME: [a-zA-Z0-9_./]*\n\n"
    GET_RESPONSE = "SERVER: %s\nFILENAME: %s\n\n"

    def __init__(self, port_use=None):
        TCPServer.__init__(self, port_use, self.handler)
        # TODO Create the DB tables if they don't exist

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

        # TODO Check that the path exists, maybe sqlite db?
        path, file = os.path.split(full_path)
        name, ext = os.path.splitext(file)
        filename = hashlib.sha256(full_path).hexdigest() + ext
        host = self.find_host(path)

        return_string = self.GET_RESPONSE % (host, filename)
        print return_string
        con.sendall(return_string)
        return

    def find_host(self, path):
        # TODO Find a file server based on the files path
        return self.HOST


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
