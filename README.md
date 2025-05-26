# Networked ASCII "Battle Game"

## Quickstart Guide:

- Make sure you have Python installed on your computer.
- Open a terminal for the server and open 1-4 more terminals for clients.
- Run the server by typing `python server.py <PORT>`. (e.g., `python server.py 12345`)
- Now to connect with one or more clients, open a new terminal and type `python client.py <SERVER IP> <PORT>`. (e.g., `python client.py 127.0.0.1 12345`)

Once connected, you can use various game commands to play the game (which are listed below).

#### Notes:

- The server will not accept more than 4 clients.
- Players are automatically assigned a unique ID (A, B, C, D) when they connect to the server.
- Game grid is a 5x5 grid.
- Obstacles are represented by `#` and health potions are represented by `+` on the grid.
- For troubleshooting ensure all clients are connected to the same IP and port.

---

## Gameplay / Command Overview:

#### Server

- Listens on a TCP socket.
- Accepts up to 4 clients.
- Maintains a **GameState** (a 2D grid).
- Supports commands like **MOVE**, **ATTACK**, **QUIT** and **JUMP**
- After each valid command, it **broadcasts** the updated game state to all players.

#### Client

- Connects to the server via TCP.
- Sends user-typed commands.
- Continuously **receives** and displays updates of the ASCII grid (plus any extra info).

#### Game Logic

- 2D grid (e.g., 5×5).
- **Obstacles** (`#`) block movement.
- **Players** are labeled `'A', 'B', 'C', 'D'`.
- **Attacks**: Deducts 10 HP from adjacent players (Affects all players 1 cell up, down, left or right from the player who attacks).
- **Quit**: On `QUIT`, the client disconnects, and the server updates the state accordingly.

#### Basic Commands

- ` MOVE <direction>`: Moves the player in the specified direction.
  - `MOVE UP`: Moves the player up one cell.
  - `MOVE DOWN`: Moves the player down one cell.
  - `MOVE LEFT`: Moves the player left one cell.
  - `MOVE RIGHT`: Moves the player right one cell.
- `ATTACK`: Attacks any player in a grid cell to the left, right, below or above the player using the ATTACK command.
- `QUIT`: Quits the game.  


#### Additional Features

- ` JUMP <direction>`: Allows the player to move 2 cells forward in the specified direction, given there is no obstacle in that cell, and the cell is within the grid. For example, the command JUMP LEFT will allow the player to move 2 cells left rather than 1, given the resulting cell is within the grid and no obstacle exists at that cell.
  - `JUMP UP`: Moves the player up two cells.
  - `JUMP DOWN`: Moves the player down two cells.
  - `JUMP LEFT`: Moves the player left two cells.
  - `JUMP RIGHT`: Moves the player right two cells.
- ` SAY <message>`: Allows the player to send messages to all other players
  - Outputs in the following format:
    **_ Player0: message _**
  - Does not broadcast message to the original sender
- Pick Up Health Boost Feature
  - If a player moves or jumps into a cell that has a health boost (`+`), the player will have their HP increase by 5 points
  - Health boosts are scattered throughout the grid
