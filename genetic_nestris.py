from game_no_screen import Game
from piece import Piece
import os
import concurrent.futures
import random
import json

MAX_GAMES = 5 # 5
POPULATION_SIZE = 32 # 32
GENERATIONS = 25 # 25

def update_next_piece(game):
    game.curr_piece.update_placement(game.curr_piece, game.curr_piece.color, game.board)
    game.next_piece = Piece(game.curr_piece.letter_index)

def piece_landed(game):
    lines_cleared = game.board.clear_lines()
    if lines_cleared > 0:
        game.cleared_lines = True
    else:
        game.cleared_lines = False
    game.board.score += game.board.calculate_points(lines_cleared)

    game.curr_piece = game.next_piece
    
    if game.check_loss():
        game.running = False

def get_best_position(all_boards, LINES_CONSTANT, HOLES_CONSTANT, HEIGHT_CONSTANT, BUMPINESS_CONSTANT, LINE_DEPENDENCY_CONSTANT):
    max_score = float('-inf')
    best_position = None
    for board, col, orientation, piece in all_boards:
        lines_cleared = board.clear_lines()

        bumpiness, height = board.get_bumpiness()
        holes = board.get_holes()

        line_dependencies = board.get_line_dependencies()
        if line_dependencies < 2:
            line_dependencies = 1
        else:
            line_dependencies = -1
        
        score = (lines_cleared * LINES_CONSTANT) - (holes * HOLES_CONSTANT) - (height * HEIGHT_CONSTANT) - (bumpiness * BUMPINESS_CONSTANT) + (line_dependencies * LINE_DEPENDENCY_CONSTANT)

        if score > max_score:
            max_score = score
            best_position = (col, orientation)

    return best_position

def run_games(starting_level):
    # Define your constants here
    LINES_CONSTANT = random.uniform(0, 1)  # Replace with actual ranges
    HOLES_CONSTANT = random.uniform(0, 1)
    HEIGHT_CONSTANT = random.uniform(0, 1)
    BUMPINESS_CONSTANT = random.uniform(0, 1)
    LINE_DEPENDENCY_CONSTANT = random.uniform(0, 1)

    # Read scores from scores.txt and keep them sorted in descending order
    scores = []
    game = Game(starting_level)

    n_games = 0

    all_boards = game.curr_piece.get_all_boards(game.board)
    best_position = get_best_position(all_boards, LINES_CONSTANT, HOLES_CONSTANT, HEIGHT_CONSTANT, BUMPINESS_CONSTANT, LINE_DEPENDENCY_CONSTANT)
    game.curr_piece.update_placement(game.curr_piece, game.curr_piece.color, game.board)
    moved = False

    increments_of_100k = 100000

    while game.running:
        if moved:
            game.run()
        else:
            game.run(best_position)
            moved = True

        if not game.curr_piece.can_move:
            piece_landed(game)
            if game.running:
                all_boards = game.curr_piece.get_all_boards(game.board)
                best_position = get_best_position(all_boards, LINES_CONSTANT, HOLES_CONSTANT, HEIGHT_CONSTANT, BUMPINESS_CONSTANT, LINE_DEPENDENCY_CONSTANT)
                moved = False
                update_next_piece(game)
                if game.board.score - increments_of_100k > 0:
                    print(game.board.score)
                    increments_of_100k += 100000

        if not game.running:
            n_games += 1

            print('Game', n_games, 'Score', game.board.score)

            # Add the new score to the list
            scores.append(game.board.score)

            if n_games >= MAX_GAMES:
                results = {
                    "LINES_CONSTANT": LINES_CONSTANT,
                    "HOLES_CONSTANT": HOLES_CONSTANT,
                    "HEIGHT_CONSTANT": HEIGHT_CONSTANT,
                    "BUMPINESS_CONSTANT": BUMPINESS_CONSTANT,
                    "LINE_DEPENDENCY_CONSTANT": LINE_DEPENDENCY_CONSTANT,
                    "average_score": sum(scores) / len(scores)
                }
                return results

            game = Game(starting_level)
            all_boards = game.curr_piece.get_all_boards(game.board)
            best_position = get_best_position(all_boards, LINES_CONSTANT, HOLES_CONSTANT, HEIGHT_CONSTANT, BUMPINESS_CONSTANT, LINE_DEPENDENCY_CONSTANT)
            game.curr_piece.update_placement(game.curr_piece, game.curr_piece.color, game.board)
            moved = False

def create_child(parent1, parent2, mutation_rate):
    # Crossover: Combine parameters from parents
    child = {}
    for key in parent1:
        if random.random() < 0.5:
            child[key] = parent1[key]
        else:
            child[key] = parent2[key]

    # Mutation: Introduce randomness
    for key in child:
        if random.random() < mutation_rate:
            child[key] = random.uniform(0, 1)  # You can adjust the mutation range

    return child

def evolve_population(population, mutation_rate):
    # Sort individuals by average score in descending order
    sorted_population = sorted(population, key=lambda x: x['average_score'], reverse=True)

    # Elitism: Carry over the top-performing individuals
    num_elites = POPULATION_SIZE // 8 # You can adjust the number of elites to keep
    new_population = sorted_population[:num_elites]

    # Create children to fill the remaining population
    while len(new_population) < POPULATION_SIZE:
        parent1, parent2 = random.choices(sorted_population, k=2)  # Select random parents
        child = create_child(parent1, parent2, mutation_rate)
        new_population.append(child)

    return new_population

if __name__ == "__main__":
    starting_level = 29
    mutation_rate = 0.1  # Adjust as needed

    population = []  # Initialize the population

    for _ in range(GENERATIONS):
        lst_of_result_dicts = []
        with concurrent.futures.ThreadPoolExecutor(max_workers=POPULATION_SIZE) as executor:
            # Launch tasks for each individual in the population and collect the results
            futures = [executor.submit(run_games, starting_level) for _ in range(POPULATION_SIZE)]
            for future in concurrent.futures.as_completed(futures):
                result = future.result()
                lst_of_result_dicts.append(result)
                print(result)
                
        print("WE MADE IT")
        # Extend the population with the results
        population.extend(lst_of_result_dicts)

        # Evolve the population for the next generation
        population = evolve_population(population, mutation_rate)

    # Sort the population one more time for the final results
    sorted_population = sorted(population, key=lambda x: x['average_score'], reverse=True)

    # Create a list of dictionaries with constants and scores
    final_results = [{'constants': {
        "LINES_CONSTANT": agent['LINES_CONSTANT'],
        "HOLES_CONSTANT": agent['HOLES_CONSTANT'],
        "HEIGHT_CONSTANT": agent['HEIGHT_CONSTANT'],
        "BUMPINESS_CONSTANT": agent['BUMPINESS_CONSTANT'],
        "LINE_DEPENDENCY_CONSTANT": agent['LINE_DEPENDENCY_CONSTANT']
        }, 'average_score': agent['average_score']} for agent in sorted_population]

    # Save the final results to a JSON file
    with open('final_results.json', 'w') as json_file:
        json.dump(final_results, json_file, indent=4)