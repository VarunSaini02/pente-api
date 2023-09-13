import flask
import json
from itertools import product

app = flask.Flask(__name__)

games = []

class PenteGame:
    def __init__(self, game_id, is_ai_x):
        self.is_ai_x = is_ai_x
        self.game_id = game_id
        self.next_player = "X"
        self.board = [["-" for j in range(19)] for i in range(19)]
        self.capturedX = 0
        self.capturedO = 0

    def get_game_state(self):
        print(self.board)
        return "#".join((self.next_player, "".join(("".join(row) for row in self.board)), str(self.capturedX), str(self.capturedO)))
    
    def get_potential_capture_endpoints(self, row, col, player):
        rows = (row - 3, row - 1, row + 1)
        cols = (col - 3, col - 1, col + 1)
        poss_endpoints = product(rows, cols)
        print(poss_endpoints)

    
    def do_move(self, row, col, player):
        # place the stone
        self.board[(row - 1)][(col - 1)] = player

        # update internal state


        
        # check for a win also

        



@app.route("/newgame/<player>")
def make_new_game(player):
    if (player != "X" and player != "O"):
        return "Player must be 'X' or 'O'"
    
    game_id = len(games)
    game = PenteGame(game_id, player == "X")
    
    games.append(PenteGame(game_id, player == "X"))

    # If AI is X, start with a move
    if (player == "X"):
        game.do_move(5, 5, player)

    return json.dumps({
        "ID": game.game_id,
        "state": game.get_game_state()
    })

if __name__ == "__main__":
    host = "localhost"
    port = 5000
    app.run(host = host, port = port, debug = True)