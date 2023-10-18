from game import Game
from piece import Piece
# from agent import Agent
import os
import pygame
from helper import plot
import copy

scores_file = "ai_scores.txt"

# agent = Agent()
scores = []
plot_scores = []
plot_mean_scores = []

def update_next_piece(game):
    game.curr_piece.update_placement(game.curr_piece, game.curr_piece.color, game.board)
    game.next_piece = Piece(game.curr_piece.letter_index)

    game.display_next_piece(game.next_piece)

def piece_landed(game):
    lines_cleared = game.board.clear_lines()
    if lines_cleared > 0:
        game.cleared_lines = True
    else:
        game.cleared_lines = False
    game.board.score += game.board.calculate_points(lines_cleared)

    game.display_score()
    game.display_lines_cleared()
    game.display_level()
    pygame.display.update()

    game.curr_piece = game.next_piece
    
    if game.check_loss():
        game.running = False

def get_best_position(all_boards):
    max_score = float('-inf')
    best_position = None
    for board, col, orientation, piece in all_boards:
        lines_cleared = board.clear_lines()
        bumpiness, height = board.get_bumpiness()
        holes = board.get_holes()
        lines_cleared_additive = lines_cleared
        if lines_cleared == 3:
            lines_cleared_additive *= 5
        elif lines_cleared == 4:
            lines_cleared_additive *= 10
        elif lines_cleared > 0:
            lines_cleared_additive *= 3
        score = lines_cleared_additive - holes - height

        if score > max_score:
            max_score = score
            best_position = (col, orientation)
    return best_position

def main(starting_level):
    # Read scores from scores.txt and keep them sorted in descending order
    scores = read_scores()
    scores.sort(reverse=True)
    record = scores[0]
    game = Game(record, starting_level)

    n_games = 0

    all_boards = game.curr_piece.get_all_boards(game.board)
    best_position = get_best_position(all_boards)
    game.curr_piece.update_placement(game.curr_piece, game.curr_piece.color, game.board)
    moved = False

    first_run = True

    while game.running:
        # state_old = agent.get_state(game.board, game.curr_piece, game.next_piece)
        # final_move = agent.get_action(state_old)
        if moved:
            game.run()
        else:
            game.run(best_position)
            moved = True

        if not game.curr_piece.can_move:
            # state_new = agent.get_state(game.board, game.curr_piece, game.next_piece)
            # agent.train_short_memory(state_old, final_move, reward, state_new, not game.running)
            # agent.remember(state_old, final_move, reward, state_new, not game.running)

            piece_landed(game)
            if game.running:
                all_boards = game.curr_piece.get_all_boards(game.board)
                best_position = get_best_position(all_boards)
                moved = False
                update_next_piece(game)
            #print(game.board.score)
            if first_run:
                game.running = False
                first_run = False

        if not game.running:
            # agent.n_games += 1
            # agent.train_long_memory()

            # if game.board.score > record:
            #     record = game.board.score
            #     agent.model.save()

            n_games += 1

            print('Game', n_games, 'Score', game.board.score, 'Record:', record)

            plot_scores.append(game.board.score)
            mean_score = game.board.score / n_games
            plot_mean_scores.append(mean_score)
            plot(plot_scores, plot_mean_scores)

            # Add the new score to the list
            scores.append(game.board.score)
            scores.sort(reverse=True)  # Sort scores in descending order

            # Write the updated scores back to scores.txt
            write_scores(scores)

            scores = read_scores()
            scores.sort(reverse=True)

            game = Game(record, starting_level)
            all_boards = game.curr_piece.get_all_boards(game.board)
            best_position = get_best_position(all_boards)
            game.curr_piece.update_placement(game.curr_piece, game.curr_piece.color, game.board)
            moved = False


def read_scores():
    scores = []
    if os.path.exists(scores_file):
        with open(scores_file, "r") as file:
            for line in file:
                score = int(line)
                scores.append(score)
    return scores

def write_scores(scores):
    with open(scores_file, "w") as file:
        for score in scores:
            file.write(str(score) + "\n")

if __name__ == "__main__":
    # Create "scores.txt" if it doesn't exist
    if not os.path.exists(scores_file):
        with open(scores_file, "w") as file:
            file.write("0")
        
    starting_level = 29

    while True:
        main(starting_level)

# if game.curr_piece.can_move:
#     test_board = copy.deepcopy(game.board)
#     test_curr_piece = copy.deepcopy(game.curr_piece)
#     test_next_piece = copy.deepcopy(game.next_piece)
#     while test_curr_piece.can_move:
#         test_curr_piece.move_down(test_board)
#     bumpiness, double_well, bearable_height = test_board.get_bumpiness()
#     holes = test_board.get_holes()
#     reward = (WELL_COEFFICIENT * double_well) - (HOLE_COEFFICIENT * holes) + (HEIGHT_COEFFICIENT * bearable_height) - bumpiness
#     state_new = agent.get_state(test_board, test_curr_piece, test_next_piece)
#     agent.train_short_memory(state_old, final_move, reward, state_new, game.done)
#     agent.remember(state_old, final_move, reward, state_new, game.done)
# else:
#     lines_cleared = piece_landed(game)
#     bumpiness, double_well, bearable_height = game.board.get_bumpiness()
#     holes = game.board.get_holes()
#     reward = (WELL_COEFFICIENT * double_well) - (HOLE_COEFFICIENT * holes) + (HEIGHT_COEFFICIENT * bearable_height) - bumpiness + lines_cleared

#     state_new = agent.get_state(game.board, game.curr_piece, game.next_piece)
#     agent.train_short_memory(state_old, final_move, reward, state_new, game.done)
#     agent.remember(state_old, final_move, reward, state_new, game.done)

#     update_next_piece(game)