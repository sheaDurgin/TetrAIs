from game import Game
from piece import Piece
from agent import Agent
import os
import pygame
from helper import plot

WELL_COEFFICIENT = 5
HOLE_COEFFICIENT = 1
HEIGHT_COEFFICIENT = 5

scores_file = "ai_scores.txt"

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

    return lines_cleared

def main(starting_level):
    # Read scores from scores.txt and keep them sorted in descending order
    scores = read_scores()
    scores.sort(reverse=True)
    game = Game(scores[0], starting_level)
    plot_scores = []
    plot_mean_scores = []
    if game.done:
        return -1
    agent = Agent()
    while game.running:
        state_old = agent.get_state(game)
        final_move = agent.get_action(state_old)

        game.run(final_move)

        if not game.curr_piece.can_move:
            lines_cleared = piece_landed(game)
            print(lines_cleared)
            bumpiness, double_well, bearable_height = game.board.get_bumpiness()
            holes = game.board.get_holes()
            reward = (WELL_COEFFICIENT * double_well) - (HOLE_COEFFICIENT * holes) + (HEIGHT_COEFFICIENT * bearable_height) - bumpiness + lines_cleared

            state_new = agent.get_state(game)
            agent.train_short_memory(state_old, final_move, reward, state_new, game.done)
            agent.remember(state_old, final_move, reward, state_new, game.done)
        
            update_next_piece(game)

        if game.done:
            agent.n_games += 1
            agent.train_long_memory()

            if game.board.score > record:
                record = game.board.score
                agent.model.save()

            print('Game', agent.n_games, 'Score', game.board.score, 'Record:', record)

            plot_scores.append(game.board.score)
            mean_score = game.board.score / agent.n_games
            plot_mean_scores.append(mean_score)
            plot(plot_scores, plot_mean_scores)

            # Add the new score to the list
            scores.append(game.board.score)
            scores.sort(reverse=True)  # Sort scores in descending order

            # Write the updated scores back to scores.txt
            write_scores(scores)

            scores = read_scores()
            scores.sort(reverse=True)

            game = Game(scores[0], starting_level)

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
        
    starting_level = 18

    while True:
        main(starting_level)