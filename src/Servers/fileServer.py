# Lab2Server.py
# Project CS4032
# Cathal Geoghegan #11347076

import socket
import os
import re
import sys
import base64

from tcpServer import TCPServer


class FileServer(TCPServer):
    UPLOAD_REGEX = "UPLOAD: [a-zA-Z0-9_.]*\nDATA: .*\n\n"
    DOWNLOAD_REGEX = "DOWNLOAD: [a-zA-Z0-9_.]*\n\n"
    DOWNLOAD_RESPONSE = "DATA: %s\n\n"
    UPLOAD_RESPONSE = "OK: 0\n\n"
    # TODO Add some error responses
    SERVER_ROOT = os.getcwd()
    BUCKET_NAME = "DirectoryServerFiles"
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
        filename = request[0].split()[1]
        data = request[1].split()[1]
        data = base64.b64decode(data)

        path = os.path.join(self.BUCKET_LOCATION, filename)
        file_handle = open(path, "w+")
        file_handle.write(data)

        return_string = self.UPLOAD_RESPONSE
        con.sendall(return_string)
        return

    def download(self, con, addr, text):
        # Handler for file download requests
        request = text.splitlines()
        filename = request[0].split()[1]

        path = os.path.join(self.BUCKET_LOCATION, filename)
        file_handle = open(path, "w+")
        data = file_handle.read()
        return_string = self.DOWNLOAD_RESPONSE % (base64.b64encode(data))
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
