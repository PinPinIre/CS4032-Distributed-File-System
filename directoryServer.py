# Lab2Server.py
# Project CS4032
# Cathal Geoghegan #11347076

import socket
import re
import sys

from server import TCPServer


class DirectoryServer(TCPServer):
    GET_REGEX = "GET_SERVER: \nFILENAME: [a-zA-Z0-9_./]*\n\n"
    GET_RESPONSE = "SERVER: %s\nFILENAME:%s\n\n"

    def __init__(self, port_use=None):
        TCPServer.__init__(self, port_use, self.handler)

    def handler(self, message, con, addr):
        if re.match(self.GET_REGEX, message):
            self.get_server(con, addr, message)
        else:
            return False
        return True

    def get_server(self, con, addr, text):
        # Handler for file upload requests
        request = text.splitlines()
        filename = request[1].split()[1]

        server = filename[::-1]

        return_string = self.GET_RESPONSE % (self.HOST, server)
        con.sendall(return_string)
        return


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
