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


class TCPServer:
    PORT = 8000
    HOST = '0.0.0.0'
    LENGTH = 4096
    MAX_THREAD = 2
    JOIN_REGEX = "JOIN_CHATROOM: [a-zA-Z0-9_]*\nCLIENT_IP: 0\nPORT: 0\nCLIENT_NAME: [a-zA-Z0-9_]*"
    LEAVE_REGEX = "LEAVE_CHATROOM: [0-9]*\nJOIN_ID: [0-9]*\nCLIENT_NAME: [a-zA-Z0-9_]*"
    HELO_REGEX = "HELO .*"
    MESSAGE_REGEX = "CHAT: [0-9]*\nJOIN_ID: [0-9]*\nCLIENT_NAME: [a-zA-Z0-9_]*\nMESSAGE: [a-zA-Z0-9_]*'\n\n']"
    JOIN_REQUEST_RESPONSE = "JOINED_CHATROOM: %s\nSERVER_IP: %s\nPORT: %s\nROOM_REF: %d\nJOIN_ID: %d\n\n"
    LEAVE_REQUEST_RESPONSE = "LEFT_CHATROOM: %s\nJOIN_ID: %s\n\n"
    HELO_RESPONSE = "HELO %s\nIP:%s\nPort:%s\nStudentID:11347076\n\n"

    def __init__(self, port_use=None):
        self.rooms = dict()
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

    def join(self, con, addr, text):
        request = text.splitlines()
        room_name = request[0].split()[1]
        client_name = request[3].split()[1]

        hash_room_name = int(hashlib.md5(room_name).hexdigest(), 16)
        hash_client_name = int(hashlib.md5(client_name).hexdigest(), 16)

        if hash_room_name not in self.rooms:
            self.rooms[hash_room_name] = dict()
        if hash_client_name not in self.rooms[hash_room_name].keys():
            self.rooms[hash_room_name][hash_client_name] = con
        return_string = self.JOIN_REQUEST_RESPONSE % (room_name, "SERVER IP", "PORT", hash_room_name, hash_client_name)
        con.sendall(return_string)
        return

    def leave(self, con, addr, text):
        request = text.splitlines()
        room_id = request[0].split()[1]
        client_id = request[1].split()[1]
        client_name = request[2].split()[1]
        """TODO: Remove the client from the room dict"""
        return_string = self.LEAVE_REQUEST_RESPONSE % (room_id, client_id)
        con.sendall(return_string)
        print client_name + " LEAVING"
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
        while True:
            data = con.recv(1024)
            message += data
            if len(data) < self.buffer_length:
                break

        # If valid http request with message body
        if len(message) > 0:
            if message == "KILL_SERVICE":
                print "Killing service"
                self.kill_serv(con)
            elif re.match(self.server.HELO_REGEX, message):
                self.server.helo(con, addr, message[5:])
            elif re.match(self.server.JOIN_REGEX, message):
                self.server.join(con, addr, message)
            elif re.match(self.server.LEAVE_REGEX, message):
                self.server.leave(con, addr, message)
            elif re.match(self.server.MESSAGE_REGEX, message):
                self.server.leave(con, addr, message)
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
