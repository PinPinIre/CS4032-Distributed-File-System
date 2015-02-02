CS4032-Distributed-File-System
==============================

Distributed File System assignment for CS4032 Distributed Systems in Trinity College Dublin

For this assignment I choose to implement
* File Server
* Directory Server
* Lock Server
* Replication

File Server
--------
The file-server uses a flat directory structure to store files. This means that all files uploaded must have a unique name.
To ensure this the path and name of the file should be hashed before uploading. An upload download model is used so the 
files are download before access and uploaded after access. The files are also sent in a message header where the data has
been base64 encoded before transmission.

Directory Server
--------
The directory server keeps track of each directory and maps directories to servers. When a client wishes to access a file
they send the path of the file and the server responds with the address & port of the server, the name of the file on the 
file-server and a list of slave servers which also contain the file. The client can read from any of these slaves but must
write to the primary server to ensure consistency. 

Lock Server
--------
The lock server assumes that each client will contact the server if they wish to write to a file. If the file is unlocked
the server responds with the timestamp of the time that the file will be locked until to. If the file is already locked, the
server responds with a fail message. It is up to the client to retry to lock again after a time has passed. When the client
has closed a file they can send a message to the lock server to unlock the file

Replication
--------
The Primary copy model was used for replication. Every time a write occurs the primary server contacts the directory server
to get the address of all the slave servers. The primary server then contacts all of slaves to update their copy of the file.


Running
--------
To test this program the start.sh file will create all directories and databases required to run the servers. It will then 
launch the directory, lock, and 3 file-servers. The client proxy in src/Client can then be used to access files.


