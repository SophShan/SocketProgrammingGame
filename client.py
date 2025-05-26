#!/usr/bin/env python3
"""
client.py
Skeleton for a networked ASCII "Battle Game" client in Python.

1. Connect to the server via TCP.
2. Continuously read user input (MOVE, ATTACK, QUIT).
3. Send commands to the server.
4. Spawn a thread to receive and display the updated game state from the server.

Usage:
   python client.py <SERVER_IP> <PORT>
"""

import sys
import socket
import threading
import time

BUFFER_SIZE = 1024
g_serverSocket = None  # shared by main thread and receiver thread

###############################################################################
# TODO: continuously receive updates (ASCII grid) from the server
###############################################################################
# def receiverThread():
#     global g_serverSocket
#     while True:
#         try:
#             received_data = g_serverSocket.recv(BUFFER_SIZE)

#             if not received_data:
#                 print("no data received")
#                 break

#             data_decoded = received_data.decode('utf-8')
#             print(data_decoded)

#         except (socket.error, ConnectionResetError):  # catch errors
#             break 

#     g_serverSocket.close()
#     sys.exit(0)

def receiverThread():
    global g_serverSocket
    global checkDisconnect

    while True:
        try:
            received_data = g_serverSocket.recv(BUFFER_SIZE) #receive data from the server

            # if data is none
            if not received_data:
                print("Server disconnected.")
                checkDisconnect = True
                break
            msg = received_data.decode('utf-8') #decode the data
            # don't print the actual SAY part if say command
            if msg.startswith("SAY "):
                print (msg[4:])
            else:
                print(msg)  
        
        except (socket.error, ConnectionResetError):
            print("Connection lost.")
            break 

    g_serverSocket.close()
    sys.exit(0)


###############################################################################
# main: connect to server, spawn receiver thread, send commands in a loop
###############################################################################
def main():
    global g_serverSocket
    global checkDisconnect
    checkDisconnect = False

    if len(sys.argv) != 3:
        print(f"Usage: {sys.argv[0]} <SERVER_IP> <PORT>")
        sys.exit(1)

    serverIP = sys.argv[1] #get the server IP
    port = int(sys.argv[2]) #get the server port

    # Create socket & connect to server
    g_serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    g_serverSocket.connect((serverIP, port))

    print(f"Connected to server {serverIP}:{port}")

    # Spawn receiver thread
    t = threading.Thread(target=receiverThread, args=())
    t.daemon = True
    t.start()

    # Main loop: read commands, send to server
    while True:
        time.sleep(0.1) #  delay to avoid going on to next command before change in checkDisconnect is rendered
        if checkDisconnect == True:
            break

        try:
            cmd = input("Enter command (MOVE/ATTACK/QUIT): ")
        except EOFError:
            # e.g., Ctrl+D
            print("Exiting client.")
            break

        if not cmd:  # empty line
            continue

        # send command to server
        g_serverSocket.sendall(cmd.encode('utf-8'))
        
        # If QUIT => break
        if cmd.upper().startswith("QUIT"):
            break

    # cleanup
    if g_serverSocket:
        g_serverSocket.close()
    sys.exit(0)

if __name__ == "__main__":
    main()
