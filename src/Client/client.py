# Lab2Client.py
# Project CS4032
# Cathal Geoghegan #11347076

import socket
import sys
import os
import re
import threading
import time
import Queue
import base64

UPLOAD_REGEX = "upload [a-zA-Z0-9_]*."
DOWNLOAD_REGEX = "download [a-zA-Z0-9_]*."
DIRECTORY_REGEX = "dir [a-zA-Z0-9_/.]*"
LOCK_REGEX = "lock [a-zA-Z0-9_/.]* [0-9]*"


class TCPClient:
    PORT = 8000
    HOST = "0.0.0.0"
    DIR_PORT = 8005
    FILE_PORT = 8006
    LOCK_PORT = 8007
    DIR_HOST = HOST
    LOCK_HOST = HOST
    UPLOAD_HEADER = "UPLOAD: %s\nDATA: %s\n\n"
    DOWNLOAD_HEADER = "DOWNLOAD: %s\n\n"
    DIRECTORY_HEADER = "GET_SERVER: \nFILENAME: %s\n\n"
    SERVER_RESPONSE = "PRIMARY_SERVER: .*\nPORT: .*\nFILENAME: .*"
    LOCK_HEADER = "LOCK_FILE: %s\nTime: %d\n\n"
    LOCK_RESPONSE = "LOCK_RESPONSE: \nFILENAME: .*\nTIME: .*\n\n"
    FAIL_RESPONSE = "ERROR: .*\nMESSAGE: .*\n\n"
    UNLOCK_HEADER = "UNLOCK_FILE: %s\n\n"
    REQUEST = "%s"
    LENGTH = 4096
    CLIENT_ROOT = os.getcwd()
    BUCKET_NAME = "ClientFiles"
    BUCKET_LOCATION = os.path.join(CLIENT_ROOT, BUCKET_NAME)

    def __init__(self, port_use=None):
        if not port_use:
            self.port_use = self.PORT
        else:
            self.port_use = port_use
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.open_files = {}
        self.threadQueue = Queue.Queue()

    def open(self, filename):
        file_downloaded = False
        if filename not in self.open_files.keys():
            request = self.__get_directory(filename)
            if re.match(self.SERVER_RESPONSE, request):
                params = request.splitlines()
                server = params[0].split()[1]
                port = int(params[1].split()[1])
                open_file = params[2].split()[1]
                self.__lock_file(filename, 10)
                file_downloaded = self.__download_file(server, port, open_file)
                if file_downloaded:
                    self.open_files[filename] = open_file
        return file_downloaded

    def close(self, filename):
        file_uploaded = False
        if filename in self.open_files.keys():
            request = self.__get_directory(filename)
            if re.match(self.SERVER_RESPONSE, request):
                self.__unlock_file(filename)
                params = request.splitlines()
                server = params[0].split()[1]
                port = int(params[1].split()[1])
                open_file = params[2].split()[1]
                file_uploaded = self.__upload_file(server, open_file)
                if file_uploaded:
                    del self.open_files[filename]
        return file_uploaded

    def read(self, filename):
        if filename in self.open_files.keys():
            local_name = self.open_files[filename]
            path = os.path.join(self.BUCKET_LOCATION, local_name)
            file_handle = open(path, "rb")
            data = file_handle.read()
            return data
        return None

    def write(self, filename, data):
        success = False
        if filename in self.open_files.keys():
            local_name = self.open_files[filename]
            path = os.path.join(self.BUCKET_LOCATION, local_name)
            file_handle = open(path, "wb+")
            file_handle.write(data)
            success = True
        return success

    def __send_request(self, data, server, port):
        return_data = ""
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        sock.connect((server, port))
        sock.sendall(self.REQUEST % data)

        # Loop until all data received
        while "\n\n" not in return_data:
            data = sock.recv(self.LENGTH)
            if len(data) == 0:
                break
            return_data += data

        # Close and dereference the socket
        sock.close()
        sock = None
        return return_data

    def __raw_request(self, string):
        """Capitilise a string by sending a request to a server"""
        return_data = ""
        # Do nothing if the string is empty or socket doesn't exist
        if len(string) > 0:
            # Create socket if it doesn't exist
            return_data = self.__send_request(string + "\n\n")
        return return_data

    def __upload_file(self, server, filename):
        """Send a request to the server to upload a file"""
        path = os.path.join(self.BUCKET_LOCATION, filename)

        file_handle = open(path, "rb")
        data = file_handle.read()
        data = base64.b64encode(data)

        request = self.UPLOAD_HEADER % (filename, data)
        return self.__send_request(request, server, self.FILE_PORT)

    def __download_file(self, server, port, filename):
        """Send a request to the server to download a file"""
        path = os.path.join(self.BUCKET_LOCATION, filename)

        request = self.DOWNLOAD_HEADER % (filename)
        request_data = self.__send_request(request, server, port).splitlines()[0]
        data = request_data.split()[0]

        data = base64.b64decode(data)
        file_handle = open(path, "wb+")
        file_handle.write(data)
        return True

    def __get_directory(self, filename):
        """Send a request to the server to create a dir"""
        request = self.DIRECTORY_HEADER % filename

        return self.__send_request(request, self.DIR_HOST, self.DIR_PORT)

    def __lock_file(self, filename, lock_time):
        """Send a request to the server to locks a file"""
        request = self.LOCK_HEADER % (filename, lock_time)
        request_data = self.__send_request(request, self.LOCK_HOST, self.LOCK_PORT)
        if re.match(self.FAIL_RESPONSE, request_data):
            request_data = request_data.splitlines()
            wait_time = float(request_data[1].split()[1])
            time.sleep(wait_time)
            self.__lock_file(filename, lock_time)
        return True

    def __unlock_file(self, filename):
        """Send a request to the server to unlock a file"""
        request = self.UNLOCK_HEADER % filename
        return self.__send_request(request, self.LOCK_HOST, self.LOCK_PORT)


class ThreadHandler(threading.Thread):
    def __init__(self, thread_queue, buffer_length, server):
        threading.Thread.__init__(self)
        self.queue = thread_queue
        self.bufferLength = buffer_length
        self.server = server

    def run(self):
        # Thread loops and waits for connections to be added to the queue
        while True:
            request = self.queue.get()
            self.handler(request)
            self.queue.task_done()

    def handler(self, (con, addr)):
        message = ""
        # Loop and receive data
        while True:
            data = con.recv(1024)
            message += data
            if len(data) < self.bufferLength:
                break

        # If valid http request with message body
        if len(message) > 0:
            print "fffa"
            # Handle diff messages
        return


def main():
    path = os.path.join(TCPClient.BUCKET_LOCATION, "test.png")
    file_handle = open(path, "rb")
    data = file_handle.read()
    try:
        if len(sys.argv) > 1 and sys.argv[1].isdigit():
            port = int(sys.argv[1])
            con = TCPClient(port)
        else:
            con = TCPClient()
    except socket.error, msg:
        print "Unable to create socket connection: " + str(msg)
        con = None
    while con:
        user_input = raw_input("Enter a message to send or type exit:")
        if user_input.lower() == "exit":
            con = None
        elif re.match(UPLOAD_REGEX, user_input.lower()):
            request = user_input.lower()
            file_name = request.split()[1]
            con.open(file_name)
            con.write(file_name, data)
            con.close(file_name)
        elif re.match(DOWNLOAD_REGEX, user_input.lower()):
            request = user_input.lower()
            file_name = request.split()[1]
            con.open(file_name)
            con.close(file_name)
        elif re.match(DIRECTORY_REGEX, user_input.lower()):
            request = user_input.lower()
            file_name = request.split()[1]
            con.open(file_name)
            con.close(file_name)
        elif re.match(LOCK_REGEX, user_input.lower()):
            request = user_input.lower()
            file_name = request.split()[1]
            con.open(file_name)
            con.close(file_name)
        else:
            data = con.__raw_request(user_input)
            print data


if __name__ == "__main__": main()
