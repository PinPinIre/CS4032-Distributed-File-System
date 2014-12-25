__author__ = 'cathalgeoghegan'
# Lab2Server.py
# Project CS4032
# Cathal Geoghegan #11347076

import socket
import os
import re
import sys
import base64

from server import TCPServer


class FileServer(TCPServer):
    UPLOAD_REGEX = "UPLOAD: [0-9]*\nFILENAME: [a-zA-Z0-9_.]*\nDATA: .*\n\n"
    DOWNLOAD_REGEX = "DOWNLOAD: [0-9]*\nFILENAME: [a-zA-Z0-9_.]*\n\n"
    SERVER_ROOT = os.getcwd()
    BUCKET_NAME = "DistBucket"
    BUCKET_LOCATION = os.path.join(SERVER_ROOT, BUCKET_NAME)

    def __init__(self, port_use=None):
        TCPServer.__init__(self, port_use, self.handler)

    def handler(self, message, con, addr):
        if re.match(self.UPLOAD_REGEX, message):
                self.upload(con, addr, message)
        elif re.match(self.DOWNLOAD_REGEX, message):
                self.download(con, addr, message)
        else:
            return False

        return True

    def upload(self, con, addr, text):
        # Handler for file upload requests
        request = text.splitlines()
        filename = request[1].split()[1]
        data = request[2].split()[1]
        data = base64.b64decode(data)

        path = os.path.join(self.BUCKET_LOCATION, filename)
        file_handle = open(path, "w+")
        file_handle.write(data)

        return_string = self.HELO_RESPONSE % ("ffafssf", addr[0], addr[1])
        con.sendall(return_string)
        return

    def download(self, con, addr, text):
        # Handler for file download requests
        request = text.splitlines()
        filename = request[1].split()[1]

        path = os.path.join(self.BUCKET_LOCATION, filename)
        file_handle = open(path, "r")
        data = file_handle.read()
        return_string = base64.b64encode(data) + "\n\n"

        con.sendall(return_string)
        return


def main():
    try:
        if len(sys.argv) > 1 and sys.argv[1].isdigit():
            port = int(sys.argv[1])
            server = FileServer(port)
        else:
            server = FileServer()
        server.listen()
    except socket.error, msg:
        print "Unable to create socket connection: " + str(msg)
        con = None


if __name__ == "__main__": main()
