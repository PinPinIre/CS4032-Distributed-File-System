# Lab2Client.py
# Project CS4032
# Cathal Geoghegan #11347076

import socket
import sys
import os
import re
import threading
import Queue
import base64


class TCPClient:
    PORT = 8000
    HOST = "0.0.0.0"
    UPLOAD_HEADER = "UPLOAD: %d\nFILENAME: %s\nDATA: %s\n\n"
    DOWNLOAD_HEADER = "DOWNLOAD: %d\nFILENAME: %s\n\n"
    DIRECTORY_HEADER = "GET_SERVER: \nFILENAME: %s\n\n"
    LOCK_HEADER = "LOCK_FILE: \nFILENAME: %s\n\n"
    UPLOAD_REGEX = "upload [a-zA-Z0-9_]*.[a-zA-Z0-9_]*"
    DOWNLOAD_REGEX = "download [a-zA-Z0-9_]*.[a-zA-Z0-9_]*"
    DIRECTORY_REGEX = "dir [a-zA-Z0-9_/.]*"
    LOCK_REGEX = "lock [a-zA-Z0-9_/.]*"
    REQUEST = "%s"
    LENGTH = 4096
    CLIENT_ROOT = os.getcwd()
    BUCKET_NAME = "DistBucketClient"
    BUCKET_LOCATION = os.path.join(CLIENT_ROOT, BUCKET_NAME)

    def __init__(self, port_use=None):
        if not port_use:
            self.port_use = self.PORT
        else:
            self.port_use = port_use
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # Create a queue of tasks with ma
        self.threadQueue = Queue.Queue()

    def send_request(self, data):
        return_data = ""
        if not self.sock:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        self.sock.connect((self.HOST, self.port_use))
        self.sock.sendall(self.REQUEST % data)

        # Loop until all data received
        while "\n\n" not in return_data:
            data = self.sock.recv(self.LENGTH)
            if len(data) == 0:
                break
            return_data += data

        # Close and dereference the socket
        self.sock.close()
        self.sock = None
        return return_data

    def raw_request(self, string):
        """Capitilise a string by sending a request to a server"""
        return_data = ""
        # Do nothing if the string is empty or socket doesn't exist
        if len(string) > 0:
            # Create socket if it doesn't exist
            return_data = self.send_request(string + "\n\n")
        return return_data

    def upload_file(self, query):
        """Send a request to the server to upload a file"""
        paramaters = query.split()
        filename = paramaters[1]
        path = os.path.join(self.BUCKET_LOCATION, filename)

        file_handle = open(path, "rb")
        data = file_handle.read()
        data = base64.b64encode(data)

        request = self.UPLOAD_HEADER % (0, filename, data)
        return self.send_request(request)

    def download_file(self, query):
        """Send a request to the server to download a file"""
        paramaters = query.split()
        filename = paramaters[1]
        path = os.path.join(self.BUCKET_LOCATION, filename)

        request = self.DOWNLOAD_HEADER % (0, paramaters[1])
        request_data = self.send_request(request).splitlines()[0]

        data = base64.b64decode(request_data)
        file_handle = open(path, "wb+")
        file_handle.write(data)
        return request_data

    def get_directory(self, query):
        """Send a request to the server to upload a file"""
        paramaters = query.split()
        filename = paramaters[1]

        request = self.DIRECTORY_HEADER % filename
        return self.send_request(request)

    def lock_file(self, query):
        """Send a request to the server to upload a file"""
        paramaters = query.split()
        filename = paramaters[1]

        request = self.LOCK_HEADER % filename
        print request
        return self.send_request(request)


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
        elif re.match(TCPClient.UPLOAD_REGEX, user_input.lower()):
            data = con.upload_file(user_input)
            #print data
        elif re.match(TCPClient.DOWNLOAD_REGEX, user_input.lower()):
            data = con.download_file(user_input)
            #print data
        elif re.match(TCPClient.DIRECTORY_REGEX, user_input.lower()):
            data = con.get_directory(user_input)
            #print data
        elif re.match(TCPClient.LOCK_REGEX, user_input.lower()):
            data = con.lock_file(user_input)
            print data
        else:
            data = con.raw_request(user_input)
            print data


if __name__ == "__main__": main()
