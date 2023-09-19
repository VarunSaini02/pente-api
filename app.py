import flask
from flask import jsonify
from itertools import product
from random import randint

app = flask.Flask(__name__)

"""
A global array containing all PenteGame objects.
"""
games = []

class PenteBoard:
    """
    Represents the board of the PenteGame. Contains convenient helper methods
    for checking and modifying the board as well as scanning for a winner.
    """
    def __init__(self, game):
        self.game = game
        self.board = ["-"] * 361
        self.captured = {
            "X": 0,
            "O": 0
        }
        self.open_spots = set(product(range(0, 19), range(0, 19)))

    def get_row_col(self, row, col):
        """
        Gets the square at (row, col).
        """
        return self.board[(row * 19) + col]

    def set_row_col(self, row, col, player):
        """
        Sets the square at (row, col).
        """
        self.board[(row * 19) + col] = player

    def update_board(self, prev_row, prev_col, prev_player):
        """
        Updates the board immediately after prev_player's most recent move.
        - Removes the most recently placed stone from self.open_spots.
        - Captures any pieces that need to be captured.
        - Checks if prev_player won on their most recent move.
        """
        if (prev_row, prev_col) in self.open_spots:
            self.open_spots.remove((prev_row, prev_col))
        self.capture_pieces(prev_row, prev_col, prev_player)
        self.check_for_win(prev_row, prev_col, prev_player)

    def get_endpoints_at_radius(self, from_row, from_col, radius):
        """
        Helper function that returns the coordinates of all squares that are the specified
        radius away from (from_row, from_col).

        Does not include squares that are out of bounds.
        """
        poss_endpoints = product((from_row - radius, from_row, from_row + radius), (from_col - radius, from_col, from_col + radius))
        endpoints = set()
        for pt in poss_endpoints:
            if 0 <= pt[0] < 19 and 0 <= pt[1] < 19 and pt != (from_row, from_col):
                endpoints.add(pt)
        return endpoints

    def capture_pieces(self, prev_row, prev_col, prev_player):
        """
        Captures any pieces that should be captured after the most recent move.
        Updates internal state as well: self.open_spots and self.captured.
        """
        potential_endpoints = self.get_endpoints_at_radius(prev_row, prev_col, 3)
        player_endpoints = set()

        for endpoint in potential_endpoints:
            if self.get_row_col(endpoint[0], endpoint[1]) == prev_player:
                potential_endpoints.add(endpoint)

        for endpoint in player_endpoints:
            row_direction = (endpoint[0] - prev_row) // 3
            col_direction = (endpoint[1] - prev_col) // 3

            first_capture_pos = (prev_row + row_direction, prev_col + col_direction)
            second_capture_pos = (prev_row + (2 * row_direction), prev_col + (2 * col_direction))

            first_capture_player = self.get_row_col(first_capture_pos[0], first_capture_pos[1])
            second_capture_player = self.get_row_col(first_capture_pos[0], first_capture_pos[1])

            other_player = "O" if prev_player == "X" else "X"

            if first_capture_player == other_player and second_capture_player == other_player:
                self.set_row_col(first_capture_pos[0], first_capture_pos[1], "-")
                self.set_row_col(second_capture_pos[0], second_capture_pos[1], "-")
                self.open_spots.add(first_capture_pos, second_capture_pos)
                self.captured[prev_player] += 2

    def check_for_win(self, prev_row, prev_col, prev_player):
        """
        Checks if prev_player won on their most recent move.
        If so, sets self.game.winner to prev_player.
        """
        if self.captured[prev_player] >= 10:
            self.game.winner = prev_player
            return

        furthest_endpoints = self.get_endpoints_at_radius(prev_row, prev_col, 4)

        for endpoint in furthest_endpoints:
            row_direction = (prev_row - endpoint[0]) // 3
            col_direction = (prev_col - endpoint[1]) // 3

            num_consecutive = 0

            for i in range(10):
                current_space = (endpoint[0] + (row_direction * i), endpoint[1] + (col_direction * i))

                # out of bounds, no need to keep checking
                if not (0 <= current_space[0] < 19 and 0 <= current_space[1] < 19):
                    break

                if self.get_row_col(current_space[0], current_space[1]) == prev_player:
                    num_consecutive += 1
                else:
                    num_consecutive = 0

                if num_consecutive == 5:
                    self.game.winner = prev_player
                    return

    def __str__(self):
        """
        Returns a string representation of this board (state and capturedX/O).
        """
        return "#".join(("".join(self.board), str(self.captured["X"]), str(self.captured["O"])))

class PenteGame:
    """
    Creates a new Pente game.
    The player field specifies the player the AI is playing as.

    Returns: a JSON object containing the game ID and game state.
    """
    def __init__(self, game_id, ai_player):
        self.ai_player = ai_player
        self.non_ai_player = "O" if ai_player == "X" else "X"
        self.game_id = game_id
        self.next_player = "X"
        self.winner = ""
        self.board = PenteBoard(self)

    def get_game_state(self):
        """
        Returns the game state as a string.
        """
        return "#".join((self.next_player, str(self.board)))

    def get_open_spot(self):
        """
        Pops and returns an open spot on the board for the AI to play.
        """
        return self.board.open_spots.pop()

    def do_move(self, row, col, is_ai_player_turn):
        """
        Executes a move on (row, col) on behalf of a player.
        - Sets the corresponding square to the player's string ("X"/"O").
        - Updates the board in response to the move.
        """
        player = self.ai_player if is_ai_player_turn else self.non_ai_player
        self.board.set_row_col(row, col, player)
        self.board.update_board(row, col, player)
        self.next_player = self.non_ai_player if is_ai_player_turn else self.ai_player

@app.route("/newgame/<player>")
def make_new_game(player):
    """
    Creates a new Pente game.
    The player field specifies the player the AI is playing as.

    Returns: a JSON object containing the game ID and game state.
    """

    if (player != "X" and player != "O"):
        return "Player must be 'X' or 'O'"

    game_id = len(games)
    game = PenteGame(game_id, player)
    games.append(game)

    # If AI is X, start with a move
    if (player == "X"):
        initial_row = randint(0, 18)
        initial_col = randint(0, 18)
        game.do_move(initial_row, initial_col, True)

    return jsonify({
        "ID": game.game_id,
        "state": game.get_game_state()
    })

@app.route("/nextmove/<gameID>/<row>/<col>")
def execute_next_move(gameID, row, col):
    """
    Takes in the (non-AI) player's next move and executes it.
    If the game has not yet been won, the AI plays a move.

    Returns: a JSON object containing the game ID, AI's last move, and game state.
    If a player has won, this function returns the winner as well.
    """

    if not (0 <= int(gameID) < len(games)):
        return "Invalid gameID"

    game = games[int(gameID)]

    if not (0 <= int(row) < 19 and 0 <= int(col) < 19):
        return "Invalid row/col pair"
    if (int(row), int(col)) not in game.board.open_spots:
        return "Space already occupied"

    if game.winner:
       return f"Game already finished, winner: {game.winner}"

    game.do_move(int(row), int(col), False)

    result = {
                "ID": game.game_id,
                "row": None,
                "col": None,
                "state": game.get_game_state(),
            }

    if not game.winner:
        ai_row, ai_col = game.get_open_spot()
        game.do_move(ai_row, ai_col, True)
        result["row"] = ai_row
        result["col"] = ai_col
        result["state"] = game.get_game_state()

    if game.winner:
        result["winner"] = game.winner

    return jsonify(result)

if __name__ == "__main__":
    host = "localhost"
    port = 5000
    app.run(host = host, port = port, debug = True)