# FileServer.py
# Project CS4032
# Cathal Geoghegan

import socket
import os
import re
import sys
import base64

from tcpServer import TCPServer


class FileServer(TCPServer):
    UPLOAD_REGEX = "UPLOAD: [a-zA-Z0-9_.]*\nDATA: .*\n\n"
    UPDATE_REGEX = "UPDATE: [a-zA-Z0-9_.]*\nDATA: .*\n\n"
    UPDATE_HEADER = "UPDATE: %s\nDATA: %s\n\n"
    DOWNLOAD_REGEX = "DOWNLOAD: [a-zA-Z0-9_.]*\n\n"
    DOWNLOAD_RESPONSE = "DATA: %s\n\n"
    GET_SLAVES_HEADER = "GET_SLAVES: %s\nPORT: %s\n\n"
    UPLOAD_RESPONSE = "OK: 0\n\n"
    SERVER_ROOT = os.getcwd()
    BUCKET_NAME = "DirectoryServerFiles"
    BUCKET_LOCATION = os.path.join(SERVER_ROOT, BUCKET_NAME)
    DIR_HOST = "0.0.0.0"
    DIR_PORT = 8005

    def __init__(self, port_use=None):
        TCPServer.__init__(self, port_use, self.handler)
        self.BUCKET_LOCATION = os.path.join(self.BUCKET_LOCATION, str(self.PORT))

    def handler(self, message, con, addr):
        if re.match(self.UPLOAD_REGEX, message):
            self.upload(con, addr, message)
        elif re.match(self.DOWNLOAD_REGEX, message):
            self.download(con, addr, message)
        elif re.match(self.UPDATE_REGEX, message):
            self.update(con, addr, message)
        else:
            return False

        return True

    def upload(self, con, addr, text):
        # Handler for file upload requests
        filename, data = self.execute_write(text)
        return_string = self.UPLOAD_RESPONSE
        con.sendall(return_string)
        self.update_slaves(filename, data)
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

    def update(self, con, addr, text):
        # Handler for file update requests
        self.execute_write(text)
        return_string = self.UPLOAD_RESPONSE
        con.sendall(return_string)
        return

    def execute_write(self, text):
        # Function that process an update/upload request and writes data to the server
        request = text.splitlines()
        filename = request[0].split()[1]
        data = request[1].split()[1]
        data = base64.b64decode(data)

        path = os.path.join(self.BUCKET_LOCATION, filename)
        file_handle = open(path, "w+")
        file_handle.write(data)
        return filename, data

    def update_slaves(self, filename, data):
        # Function that gets all the slaves and updates file on them
        slaves = self.get_slaves()
        update = self.UPDATE_HEADER % (filename, base64.b64encode(data))
        for (host, port) in slaves:
            self.send_request(update, host, int(port))
        return

    def get_slaves(self):
        # Function to get the list of slave file servers
        return_list = []
        request_data = self.GET_SLAVES_HEADER % (self.HOST, self.PORT,)
        lines = self.send_request(request_data, self.DIR_HOST, self.DIR_PORT).splitlines()
        slaves = lines[1:-1]
        for i in range(0, len(slaves), 2):
            host = slaves[i].split()[1]
            port = slaves[i + 1].split()[1]
            return_list.append((host, port))
        return return_list


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
