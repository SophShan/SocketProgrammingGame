#!/usr/bin/env python3
"""
server.py
Skeleton for a networked ASCII "Battle Game" server in Python.

1. Create a TCP socket and bind to <PORT>.
2. Listen and accept up to 4 client connections.
3. Maintain a global game state (grid + players + obstacles).
4. On receiving commands (MOVE, ATTACK, QUIT, etc.), update the game state
   and broadcast the updated state to all connected clients.

Usage:
   python server.py <PORT>
"""

import sys
import socket
import threading
import time

MAX_CLIENTS = 4
BUFFER_SIZE = 1024
GRID_ROWS = 5
GRID_COLS = 5

###############################################################################
# Data Structures
###############################################################################

# Each player can be stored as a dict, for instance:
# {
#    'x': int,
#    'y': int,
#    'hp': int,
#    'active': bool
# }

# The global game state might be stored in a dictionary:
# {
#   'grid': [ [char, ...], ... ],        # 2D list of chars
#   'players': [ playerDict, playerDict, ...],
#   'clientCount': int
# }

g_gameState = {}
g_clientSockets = [None] * MAX_CLIENTS  # track client connections
g_stateLock = threading.Lock()          # lock for the game state

###############################################################################
# Initialize the game state
###############################################################################
def initGameState():
    global g_gameState
    # Create a 2D grid filled with '.'
    grid = []
    for r in range(GRID_ROWS):
        row = ['.'] * GRID_COLS
        grid.append(row)

    # Example: place a couple of obstacles '#'
    # (Feel free to add more or randomize them.)
    grid[2][2] = '#'
    grid[1][3] = '#'

    # Placing HP potions for players
    # If a player goes to the cell with a potion, they get 5 HP
    grid[3][1] = '+'
    grid[0][4] = '+'
    grid[1][3] = '+'
    grid[2][3] = '+'

    # Initialize players
    players = []
    for i in range(MAX_CLIENTS):
        p = {
            'x': -1,
            'y': -1,
            'hp': 100,
            'active': False
        }
        players.append(p)

    g_gameState = {
        'grid': grid,
        'players': players,
        'clientCount': 0
    }

###############################################################################
# Refresh the grid with current player positions.
# We clear old player marks (leaving obstacles) and re-place them according
# to the players' (x,y).
###############################################################################
def refreshPlayerPositions():
    """Clear old positions (leaving obstacles) and place each active player."""
    grid = g_gameState['grid']
    players = g_gameState['players']

    # Clear non-obstacle cells
    for r in range(GRID_ROWS):
        for c in range(GRID_COLS):
            if grid[r][c] != '#' and grid[r][c] != '+':
                grid[r][c] = '.'

    # Place each active player
    for i, player in enumerate(players):
        if player['active'] and player['hp'] > 0:
            px = player['x']
            py = player['y']
            grid[px][py] = chr(ord('A') + i)  # 'A', 'B', 'C', 'D'

###############################################################################
# Build a string that represents the current game state (ASCII grid), 
# which you can send to all clients.
###############################################################################
def buildStateString():
    # e.g., prefix with "STATE\n", then rows of the grid, then player info
    buffer = []
    buffer.append("STATE\n")

    # Copy the grid
    board = g_gameState['grid']

    for row in board:
        for c in row:
            buffer.append(c)
        buffer.append("\n")

    #print(g_gameState['grid'])

    # ...
    # Optionally append player info to the string
    buffer.append("Players:\n")
    players = g_gameState['players']
    for i, player in enumerate(players):
        if player['active']:
            # append info from the player database
            buffer.append("  Player "+ str(i) + ": HP="+ str(player['hp']) + ' Pos = (' + str(player['x']) + ',' + str(player['y']) + ')\n')

    return ''.join(buffer)


###############################################################################
# Broadcast the current game state to all connected clients
###############################################################################

def broadcastState():
    stateStr = buildStateString().encode('utf-8')  # Encode state message
    for sock in g_clientSockets:
        if sock:
            try:
                sock.sendall(stateStr)
            except socket.error:
                print("Error sending state to a client. Closing connection.")
                sock.close()
                g_clientSockets[g_clientSockets.index(sock)] = None

###############################################################################
# Handle a client command: MOVE, ATTACK, QUIT, etc.
#  - parse the string
#  - update the player's position or HP
#  - call refreshPlayerPositions() and broadcastState()
###############################################################################
def handleCommand(playerIndex, cmd):
    with g_stateLock:
        players = g_gameState['players']

        # original player position
        ogx = players[playerIndex]['x']
        ogy = players[playerIndex]['y']

        # Example: parse "MOVE UP", "MOVE DOWN", etc.
        if cmd.startswith("MOVE"):
            if "UP" in cmd:

                # get up position coordinates
                nx = players[playerIndex]['x'] - 1
                ny = players[playerIndex]['y']

                # ensure new position is in grid and is not an obstacle or occupied by another player
                if 0 <= nx < GRID_ROWS and (g_gameState['grid'][nx][ny] == '.' or g_gameState['grid'][nx][ny] == '+'):
                   
                   # update grid and player position
                    g_gameState['grid'][ogx][ogy] = '.'  # remove player from old position
                    players[playerIndex]['x'] = nx
                    if g_gameState['grid'][nx][ny] == '+':
                        players[playerIndex]['hp'] += 5
                    g_gameState['grid'][nx][ny] = chr(ord('A') + playerIndex)  # update position of player

                # send new state to all players
                refreshPlayerPositions()
                broadcastState()
            elif "DOWN" in cmd:

                # get down position coordinates
                nx = players[playerIndex]['x'] + 1
                ny = players[playerIndex]['y']

                # ensure new position is in grid and is not an obstacle or occupied by another player
                if nx < GRID_ROWS and (g_gameState['grid'][nx][ny] == '.' or g_gameState['grid'][nx][ny] == '+'):
                    
                    # update grid and player position
                    g_gameState['grid'][ogx][ogy] = '.'  # remove player from old position
                    players[playerIndex]['x'] = nx
                    if g_gameState['grid'][nx][ny] == '+':
                        players[playerIndex]['hp'] += 5
                    g_gameState['grid'][nx][ny] = chr(ord('A') + playerIndex) # update position of player

                # send new state to all players
                refreshPlayerPositions()
                broadcastState()
            elif "LEFT" in cmd:
                # get left position coordinates
                nx = players[playerIndex]['x']
                ny = players[playerIndex]['y'] - 1

                # ensure new position is in grid and is not an obstacle or occupied by another player
                if 0 <= ny < GRID_COLS and (g_gameState['grid'][nx][ny] == '.' or g_gameState['grid'][nx][ny] == '+'):
                    
                    # update grid and player position
                    g_gameState['grid'][ogx][ogy] = '.'  # remove player from old position
                    players[playerIndex]['y'] = ny
                    if g_gameState['grid'][nx][ny] == '+':
                        players[playerIndex]['hp'] += 5
                    g_gameState['grid'][nx][ny] = chr(ord('A') + playerIndex) # update position of player

                # send new state to all players
                refreshPlayerPositions()
                broadcastState()
            elif "RIGHT" in cmd:
                # get right position coordinates
                nx = players[playerIndex]['x']
                ny = players[playerIndex]['y'] + 1

                # ensure new position is in grid and is not an obstacle or occupied by another player
                if ny < GRID_COLS and (g_gameState['grid'][nx][ny] == '.' or g_gameState['grid'][nx][ny] == '+'):
                    
                    # update grid and player position
                    g_gameState['grid'][ogx][ogy] = '.'  # remove player from old position
                    players[playerIndex]['y'] = ny
                    if g_gameState['grid'][nx][ny] == '+':
                        players[playerIndex]['hp'] += 5
                    g_gameState['grid'][nx][ny] = chr(ord('A') + playerIndex) # update position of player

                # send new state to all players
                refreshPlayerPositions()
                broadcastState()
            else:
                g_clientSockets[playerIndex].send('Invalid command'.encode('utf-8'))

        elif cmd.startswith("ATTACK"):
            # original player position
            ogx = players[playerIndex]['x']
            ogy = players[playerIndex]['y']

            # check if any player is adjacent to the player who attacked
            for i, player in enumerate(players):
                if player['active'] and player['hp'] > 0:
                    if player['x'] == ogx - 1 and player['y'] == ogy:  # if a player is 1 up
                        player['hp'] -= 10
                    elif player['x'] == ogx + 1 and player['y'] == ogy:  # if a player is 1 down
                        player['hp'] -= 10
                    elif player['x'] == ogx and player['y'] == ogy - 1:  # if a player is 1 left
                        player['hp'] -= 10
                    elif player['x'] == ogx and player['y'] == ogy + 1:  # if a player is 1 right
                        player['hp'] -= 10

                    # If a player was attacked and died
                    if player['hp'] <= 0:
                        # print to server
                        print (f"Player {chr(ord('A') + i)} has been killed by Player {chr(ord('A') + playerIndex)}") 
                        
                        # Send message to client who died
                        message = f"You were killed by Player {chr(ord('A') + playerIndex)}"
                        try:
                            g_clientSockets[i].sendall(message.encode('utf-8'))  
                        except socket.error:
                            print(f"Failed to send death message to Player {chr(ord('A') + i)}")
                        
                        time.sleep(0.5) # need a delay to send message before the connection is cut to killed player
                        
                        # close connection of killed player
                        players[i]['active'] = False
                        g_clientSockets[i].close()
                        g_clientSockets[i] = None
                        g_gameState['clientCount'] -= 1

            # show new state of game to players
            refreshPlayerPositions()
            broadcastState()

        elif cmd.startswith("QUIT"):
            print(f"Player {playerIndex} quit the game.") # print message to server

            # remove player from game
            players[playerIndex]['active'] = False
            players[playerIndex]['x'] = -1  # Remove player from grid
            players[playerIndex]['y'] = -1
            g_gameState['grid'][ogx][ogy] = '.'  # Clear player position

            if g_clientSockets[playerIndex]:  
                message = f"Player {playerIndex} has quit the game."
                try:
                    # for each player still playing
                    for i in range (len(g_clientSockets)): 
                        if g_clientSockets[i]:
                            g_clientSockets[i].sendall(message.encode('utf-8'))  # Send message
                except socket.error:
                    print(f"Failed to send Quit messages")
                
                time.sleep(0.5) # need a delay to send message before the connection is cut

                # close connection of quitting player
                g_clientSockets[playerIndex].close()
                g_clientSockets[playerIndex] = None
                g_gameState['clientCount'] -= 1

            # send new state to all players
            refreshPlayerPositions()
            broadcastState()

        elif cmd.startswith("JUMP"):  
            if "UP" in cmd:
                # get potential new position coordinates (2 cells up)
                nx = players[playerIndex]['x'] - 2
                ny = players[playerIndex]['y']

                if 0 <= nx < GRID_ROWS and (g_gameState['grid'][nx][ny] == '.' or g_gameState['grid'][nx][ny] == '+'):
                    
                    # update the grid and player's position
                    g_gameState['grid'][ogx][ogy] = '.'
                    players[playerIndex]['x'] = nx
                    if g_gameState['grid'][nx][ny] == '+':
                        players[playerIndex]['hp'] += 5
                    g_gameState['grid'][nx][ny] = chr(ord('A') + playerIndex)
                refreshPlayerPositions()
                broadcastState()
            elif "DOWN" in cmd:
                # get potential new position coordinates (2 cells down)
                nx = players[playerIndex]['x'] + 2
                ny = players[playerIndex]['y']

                # if no player occupies the cell and it is not an obstacle
                if nx < GRID_ROWS and (g_gameState['grid'][nx][ny] == '.' or g_gameState['grid'][nx][ny] == '+'):
                    
                    # update the grid and player's position
                    g_gameState['grid'][ogx][ogy] = '.'
                    players[playerIndex]['x'] = nx
                    if g_gameState['grid'][nx][ny] == '+':
                        players[playerIndex]['hp'] += 5
                    g_gameState['grid'][nx][ny] = chr(ord('A') + playerIndex)
                refreshPlayerPositions()
                broadcastState()
            elif "LEFT" in cmd:
                # get potential new position coordinates (2 cells left)
                nx = players[playerIndex]['x']
                ny = players[playerIndex]['y'] - 2

                # if no player occupies the cell and it is not an obstacle
                if 0 <= ny < GRID_COLS and (g_gameState['grid'][nx][ny] == '.' or g_gameState['grid'][nx][ny] == '+'):
                    
                    # update the grid and player's position
                    g_gameState['grid'][ogx][ogy] = '.'
                    players[playerIndex]['y'] = ny
                    if g_gameState['grid'][nx][ny] == '+':
                        players[playerIndex]['hp'] += 5
                    g_gameState['grid'][nx][ny] = chr(ord('A') + playerIndex)
                refreshPlayerPositions()
                broadcastState()
            elif "RIGHT" in cmd:
                # get potential new position coordinates (2 cells right)
                nx = players[playerIndex]['x']
                ny = players[playerIndex]['y'] + 2

                # if no player occupies the cell and it is not an obstacle
                if ny < GRID_COLS and (g_gameState['grid'][nx][ny] == '.' or g_gameState['grid'][nx][ny] == '+'):
                    
                    # update the grid and player's position
                    g_gameState['grid'][ogx][ogy] = '.'
                    players[playerIndex]['y'] = ny
                    if g_gameState['grid'][nx][ny] == '+':
                        players[playerIndex]['hp'] += 5
                    g_gameState['grid'][nx][ny] = chr(ord('A') + playerIndex)
                refreshPlayerPositions()
                broadcastState()
            else:
                g_clientSockets[playerIndex].send('Invalid command'.encode('utf-8'))
        elif cmd.startswith("SAY"):
            msg_cmd = cmd.split(' ')
            # SAY will get stripped on client end
            msg = 'SAY Player' + str(playerIndex) + ': '

            # append all words of the message exculding the SAY keyword
            for i in msg_cmd[1:]:
                msg += i
            msgStr = msg.encode('utf-8')  # Encode state message

            # send message to all other players
            for i, sock in enumerate(g_clientSockets):
                # don't send to user that the message came from
                if sock and i != playerIndex:
                    try:
                        sock.sendall(msgStr)
                    except socket.error:
                        print("Error sending message to a client. Closing connection.")
                        sock.close()
                        g_clientSockets[g_clientSockets.index(sock)] = None
            
            # send new state to all players
            refreshPlayerPositions()
            broadcastState()
        else: # if the command entered was non of the possible commands
            g_clientSockets[playerIndex].send('Invalid command'.encode('utf-8'))


        


###############################################################################
# Thread function: handle communication with one client
###############################################################################

def clientHandler(playerIndex):
    sock = g_clientSockets[playerIndex]
    with g_stateLock:
        g_gameState['players'][playerIndex]['x'] = playerIndex  # Start position
        g_gameState['players'][playerIndex]['y'] = 0 # start position
        g_gameState['players'][playerIndex]['hp'] = 100 #initial health
        g_gameState['players'][playerIndex]['active'] = True #player is active

        refreshPlayerPositions() #update the grid with the player's position
        
        sock.send(b"READY\n")  # Notify client
        broadcastState() #send the current state to all clients

    while True:
        try:
            player_command = sock.recv(BUFFER_SIZE).decode('utf-8').strip() #receive the command from the client
            if not player_command: #if the client has disconnected
                print(f"Player {playerIndex} disconnected.")
                break

            handleCommand(playerIndex, player_command) #handle the command

        except (socket.error, ConnectionResetError): #catch errors
            print(f"Error with player {playerIndex}.")
            break  

    # Cleanup on disconnect
    with g_stateLock:
        g_gameState['players'][playerIndex]['active'] = False #player is no longer active
        g_gameState['grid'][g_gameState['players'][playerIndex]['x']][g_gameState['players'][playerIndex]['y']] = '.' #remove the player from the grid
        g_clientSockets[playerIndex] = None #remove the player from the client list
        refreshPlayerPositions() #update the grid with the player's position
        broadcastState() #send the current state to all clients


###############################################################################
# main: set up server socket, accept clients, spawn threads
###############################################################################
def main():
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} <PORT>")
        sys.exit(1)

    port = int(sys.argv[1])
    initGameState()

    # Create a TCP socket and bind to <PORT>.

    # TODO: create server socket, bind, listen
    # Example:
    serverSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    serverSock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    serverSock.bind(("127.0.0.1", port))
    serverSock.listen(5)
    
    print(f"Server listening on port {port}, IP ... 127.0.0.1")

    try:

        while True:
            # TODO: accept new connection
            clientSock, addr = serverSock.accept()
            print(f"Accepted new client from {addr}")

            # 1) Lock state
            with g_stateLock:
            # 2) Check if g_gameState['clientCount'] < MAX_CLIENTS
            #    otherwise, reject
                if g_gameState['clientCount'] >= MAX_CLIENTS:
                    clientSock.send("Server is full.".encode('utf-8'))
                    clientSock.close()
                    continue
            #
            # 3) find a free slot in g_clientSockets
                slot = None
                for i in range(MAX_CLIENTS):
                    if g_clientSockets[i] is None:
                        slot = i
                        break

                g_clientSockets[slot] = clientSock
                g_gameState['clientCount'] += 1
            # 4) spawn a thread => threading.Thread(target=clientHandler, args=(slot,))

            clientThread = threading.Thread(target=clientHandler, args=(slot,))
            clientThread.daemon = True
            clientThread.start()
    except KeyboardInterrupt:
        print("Exiting server.")
    finally:
        serverSock.close() # somehow need to figure out how to end while loop

if __name__ == "__main__":
    main()
