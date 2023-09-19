"""
Ensure that app.py is running locally before running this test suite.
"""

import requests

def print_game_state(state):
    split = state.split("#")
    print("---Game State---")
    print("Next player:", split[0])
    for i in range(19):
        print(f"Row {i}\t: {split[1][i * 19 : (i + 1) * 19]}")
    print("Captured by X:", split[2])
    print("Captured by O:", split[3])
    print("----------------")

def get_api_response(api_command, *api_inputs):
    return requests.get(
        f"http://localhost:5000/{api_command}/{'/'.join(api_inputs)}"
    ).json()

# TEST CASE
def ai_makes_initial_move():
    response = get_api_response("newgame", "X")
    print_game_state(response["state"])
    state = response["state"].split("#")
    assert state[0] == "O"          # Next player is O
    assert state[1].count("X") == 1 # AI: one initial move
    assert state[2] == "0"          # No captured pieces by X
    assert state[3] == "0"          # No captured pieces by O

# TEST CASE
def player_makes_initial_move():
    response = get_api_response("newgame", "O")
    print_game_state(response["state"])
    state = response["state"].split("#")
    assert state[0] == "X"          # Next player is X
    assert state[1].count("X") == 0 # AI: no initial move
    assert state[1].count("O") == 0 # Player: no initial move (yet)
    assert state[2] == "0"          # No captured pieces by X
    assert state[3] == "0"          # No captured pieces by O

# TEST CASE
def can_access_same_game_from_id_when_ai_starts():
    id = get_api_response("newgame", "X")["ID"]
    response = get_api_response("nextmove", str(id), "0", "0")
    print_game_state(response["state"])
    state = response["state"].split("#")
    assert state[0] == "O"          # Next player is X
    assert state[1].count("X") == 2 # AI: made two moves
    assert state[1].count("O") == 1 # Player: made one move
    assert state[1][0] == "O"       # Player's move was at (0, 0)
    assert state[2] == "0"          # No captured pieces by X
    assert state[3] == "0"          # No captured pieces by O

# TEST CASE
def can_access_same_game_from_id_when_player_starts():
    id = get_api_response("newgame", "O")["ID"]
    response = get_api_response("nextmove", str(id), "0", "0")
    print_game_state(response["state"])
    state = response["state"].split("#")
    assert state[0] == "X"          # Next player is X
    assert state[1].count("O") == 1 # AI: made one move
    assert state[1].count("X") == 1 # Player: made one move
    assert state[1][0] == "X"       # Player's move was at (0, 0)
    assert state[2] == "0"          # No captured pieces by X
    assert state[3] == "0"          # No captured pieces by O

# TEST CASE
def player_can_win_with_five_in_a_row_horizontal():
    id = get_api_response("newgame", "O")["ID"]

    for i in range(5):
        response = get_api_response("nextmove", str(id), "0", str(i))

        # There is a chance that the AI blocked our attempt to win (randomly)
        # For testing purposes, we will just try again
        if "error" in response.keys() and response["error"] == "Space already occupied":
            player_can_win_with_five_in_a_row_horizontal()
            return

    print_game_state(response["state"])
    state = response["state"].split("#")
    assert state[1].count("X") == 5     # Player put down 5 Xs
    assert response["winner"] == "X"    # Player won
    assert state[0] == "O"              # "Next player" should have been the AI: "O"

# TEST CASE
def player_can_win_with_five_in_a_row_vertical():
    id = get_api_response("newgame", "O")["ID"]

    for i in range(5):
        response = get_api_response("nextmove", str(id), str(i), "0")

        # There is a chance that the AI blocked our attempt to win (randomly)
        # For testing purposes, we will just try again
        if "error" in response.keys() and response["error"] == "Space already occupied":
            player_can_win_with_five_in_a_row_vertical()
            return

    print_game_state(response["state"])
    state = response["state"].split("#")
    assert state[1].count("X") == 5     # Player put down 5 Xs
    assert response["winner"] == "X"    # Player won
    assert state[0] == "O"              # "Next player" should have been the AI: "O"

# TEST CASE
def player_can_win_with_five_in_a_row_diagonal():
    id = get_api_response("newgame", "O")["ID"]

    for i in range(5):
        response = get_api_response("nextmove", str(id), str(i), str(i))

        # There is a chance that the AI blocked our attempt to win (randomly)
        # For testing purposes, we will just try again
        if "error" in response.keys() and response["error"] == "Space already occupied":
            player_can_win_with_five_in_a_row_diagonal()
            return

    print_game_state(response["state"])
    state = response["state"].split("#")
    assert state[1].count("X") == 5     # Player put down 5 Xs
    assert response["winner"] == "X"    # Player won
    assert state[0] == "O"              # "Next player" should have been the AI: "O"

# TEST SUITE
def run_tests():
    tests = [
        ai_makes_initial_move,
        player_makes_initial_move,
        can_access_same_game_from_id_when_ai_starts,
        can_access_same_game_from_id_when_player_starts,
        player_can_win_with_five_in_a_row_horizontal,
        player_can_win_with_five_in_a_row_vertical,
        player_can_win_with_five_in_a_row_diagonal,
    ]

    for test in tests:
        print("\n--- TESTING:", test.__name__, "---")
        test()

    print("\nAll tests passed!")

if __name__ == "__main__":
    run_tests()
