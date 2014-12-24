# Lab2Client.py
# Project CS4032
# Cathal Geoghegan #11347076

import socket
import sys
import re
import threading
import Queue


class TCPClient:
    PORT = 8000
    HOST = "0.0.0.0"
    JOIN_HEADER = "JOIN_CHATROOM: %s\nCLIENT_IP: 0\nPORT: 0\nCLIENT_NAME: %s"
    LEAVE_HEADER = "LEAVE_CHATROOM: %s\nJOIN_ID: %s\nCLIENT_NAME: %s"
    JOIN_REGEX = "join [a-zA-Z0-9_]* [a-zA-Z0-9_]*"
    LEAVE_REGEX = "leave [a-zA-Z0-9_]* [a-zA-Z0-9_]* [a-zA-Z0-9_]*"
    REQUEST = "%s"
    LENGTH = 4096

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
            return_data = self.send_request(string)
        return return_data

    def join_room(self, query):
        """Send a request to the server to join a chatroom"""
        paramaters = query.split()
        request = self.JOIN_HEADER % (paramaters[1], paramaters[2])
        print request
        return self.send_request(request)

    def leave_room(self, query):
        """Send a request to the server to join a chatroom"""
        paramaters = query.split()
        request = self.LEAVE_HEADER % (paramaters[1], paramaters[2], paramaters[3])
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
        elif re.match(TCPClient.JOIN_REGEX, user_input.lower()):
            data = con.join_room(user_input)
            print data
        elif re.match(TCPClient.LEAVE_REGEX, user_input.lower()):
            data = con.leave_room(user_input)
            print data
        else:
            data = con.raw_request(user_input)
            print data


if __name__ == "__main__": main()
