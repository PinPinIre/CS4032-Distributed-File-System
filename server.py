# Lab2Server.py
# Project CS4032
# Cathal Geoghegan #11347076

import socket
import threading
import Queue
import os
import httplib
import re
import sys
import random
import hashlib
import base64


class TCPServer:
    PORT = 8000
    HOST = '0.0.0.0'
    LENGTH = 4096
    MAX_THREAD = 2
    HELO_RESPONSE = "HELO %s\nIP:%s\nPort:%s\nStudentID:11347076\n\n"
    UPLOAD_REGEX = "UPLOAD: [0-9]*\nFILENAME: [a-zA-Z0-9_.]*\nDATA: .*\n\n"
    DOWNLOAD_REGEX = "DOWNLOAD: [0-9]*\nFILENAME: [a-zA-Z0-9_.]*\n\n"
    HELO_REGEX = "HELO .*"
    SERVER_ROOT = os.getcwd()
    BUCKET_NAME = "DistBucket"
    BUCKET_LOCATION = os.path.join(SERVER_ROOT, BUCKET_NAME)
    LENGTH = 4096

    def __init__(self, port_use=None):
        if not port_use:
            port_use = self.PORT
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.bind((self.HOST, port_use))

        # Create a queue of tasks with ma
        self.threadQueue = Queue.Queue(maxsize=self.MAX_THREAD)

        # Create thread pool
        for i in range(self.MAX_THREAD):
            thread = ThreadHandler(self.threadQueue, self.LENGTH, self)
            thread.setDaemon(True)
            thread.start()
        self.listen()

    def listen(self):
        self.sock.listen(5)

        # Listen for connections and delegate to threads
        while True:
            con, addr = self.sock.accept()

            # If queue full close connection, otherwise send to thread
            if not self.threadQueue.full():
                self.threadQueue.put((con, addr))
            else:
                print "Queue full closing connection from %s:%s" % (addr[0], addr[1])
                con.close()

    def kill_serv(self, con):
        # Kill server
        os._exit(1)
        return

    def helo(self, con, addr, text):
        # Reply to helo request
        reply = text.rstrip()  # Remove newline
        return_string = self.HELO_RESPONSE % (reply, addr[0], addr[1])
        con.sendall(return_string)
        return

    def default(self, con, addr, text):
        # Default handler for everything else
        print "Default"
        return

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

class ThreadHandler(threading.Thread):
    def __init__(self, thread_queue, buffer_length, server):
        threading.Thread.__init__(self)
        self.queue = thread_queue
        self.buffer_length = buffer_length
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
        while "\n\n" not in message:
            data = con.recv(TCPServer.LENGTH)
            if len(data) == 0:
                break
            message += data

        # If valid http request with message body
        if len(message) > 0:
            print message
            if message == "KILL_SERVICE":
                print "Killing service"
                self.kill_serv(con)
            elif re.match(self.server.HELO_REGEX, message):
                self.server.helo(con, addr, message[5:])
            elif re.match(self.server.UPLOAD_REGEX, message):
                self.server.upload(con, addr, message)
            elif re.match(self.server.DOWNLOAD_REGEX, message):
                self.server.download(con, addr, message)
            else:
                self.server.default(con, addr, message)
        return


def main():
    try:
        if len(sys.argv) > 1 and sys.argv[1].isdigit():
            port = int(sys.argv[1])
            server = TCPServer(port)
        else:
            server = TCPServer()
    except socket.error, msg:
        print "Unable to create socket connection: " + str(msg)
        con = None


if __name__ == "__main__": main()
