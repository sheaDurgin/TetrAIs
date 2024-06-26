import pygame
from piece import Piece
from board import Board
import os
import sys

cell_size = 40
TOTAL_ROWS = 20
TOTAL_COLS = 10

FPS = 60

screen_width = 800
screen_height = 900

NEXT_PIECE_X = 500
NEXT_PIECE_Y = 1065

RIGHT = 1
LEFT = -1
CLOCKWISE = 1
COUNTER_CLOCKWISE = -1

WELL_COEFFICIENT = 5
HOLE_COEFFICIENT = 5
HEIGHT_COEFFICIENT = 5

frames = {
    0: 48, 1: 43, 2: 38, 3: 33, 4: 28, 5: 23, 6: 18, 
    7: 13, 8: 8, 9: 6, 10: 5, 13: 4, 16: 3, 19: 2, 29: 1
}  

offsets = {
    0: (-2, 1), 1: (-1, 1), 2: (0, 1), 3: (1, 1),
    4: (-2, 0), 5: (-1, 0), 6: (0, 0), 7: (1, 0),
    8: (-2, -1), 9: (-1, -1), 10: (0, -1), 11: (1, -1),
    12: (-2, -2), 13: (-1, -2), 14: (0, -2), 15: (1, -2),
}

class Game:
    def __init__(self, high_score, starting_level):
        self.high_score = high_score

        pygame.init()
        #self.font = pygame.font.Font(resource_path("ShortBaby-Mg2w.ttf"), 36)
        self.font = pygame.font.SysFont("comicsans", 36)
        self.screen = pygame.display.set_mode((screen_width, screen_height))
        self.screen.fill("black")
        self.first_level = starting_level
        self.running = True

        self.board = Board(self.first_level)

        self.top_left_x = (screen_width - (TOTAL_COLS * cell_size)) // 2
        self.top_left_y = screen_height - (TOTAL_ROWS * cell_size)

        self.curr_piece = Piece(-1)
        self.next_piece = Piece(self.curr_piece.letter_index)
        self.display_next_piece(self.next_piece)

        self.fall_time = 0

        self.clock = pygame.time.Clock()

        self.draw_border()
        self.display_score()
        self.display_lines_cleared()
        self.display_level()

        self.delay = 60
        self.cleared_lines = False

    def run(self, best_position=None):
        pygame.display.update()
        self.draw_board()
        self.draw_border()
        self.display_high_score()

        self.clock.tick(FPS)

        # self.move_agent(action)
        if best_position is not None:
            col, orientation = best_position

            val = True
            while self.curr_piece.orientation != orientation and val:
                val = self.curr_piece.rotate(CLOCKWISE, self.board)

            val = True
            while self.curr_piece.orientation != orientation and val:
                val = self.curr_piece.rotate(COUNTER_CLOCKWISE, self.board)

            while self.curr_piece.col < col and val:
                val = self.curr_piece.move_sideways(RIGHT, self.board) 
            while self.curr_piece.col > col and val:
                val = self.curr_piece.move_sideways(LEFT, self.board)
                
        self.fall()
        self.fall_time += 1

    # action = [MOVEMENT, ROTATION], 0 = No input, otherwise do input
    def move_agent(self, action):
        if action == [1, 0, 0, 0, 0]:
            self.curr_piece.move_sideways(RIGHT, self.board) 
        elif action == [0, 1, 0, 0, 0]:
            self.curr_piece.move_sideways(LEFT, self.board)
        elif action == [0, 0, 1, 0, 0]:
            self.curr_piece.rotate(CLOCKWISE, self.board)
        elif action == [0, 0, 0, 1, 0]:
            self.curr_piece.rotate(COUNTER_CLOCKWISE, self.board)      
    
    def fall(self):
        if self.delay == 0 and self.curr_piece.spawn_delay:
            self.delay = 10
            if self.cleared_lines:
                self.delay = 20

        if self.fall_time >= frames[self.board.frames_index] + self.delay: 
            self.fall_time = 0
            self.curr_piece.move_down(self.board)
            self.curr_piece.spawn_delay = False
            self.delay = 0

    def check_loss(self):
        for idx, block in enumerate(self.curr_piece.orientation):
            if block == '1':
                col_offset, row_offset = offsets[idx]
                spot = (self.curr_piece.col + col_offset, self.curr_piece.row + row_offset)
                if self.board.blocks[spot] != (0, 0, 0):
                    return True

    def draw_board(self):
        for row in range(TOTAL_ROWS):
            for col in range(TOTAL_COLS):
                x = self.top_left_x + col * cell_size
                y = self.top_left_y + (TOTAL_ROWS - row - 1) * cell_size  # Adjust the y-coordinate
                color = self.board.blocks[(col, row)]
                pygame.draw.rect(self.screen, color, (x, y, cell_size, cell_size))
    
    def draw_border(self):
        # Define the border rectangle
        border_rect = pygame.Rect(self.top_left_x, self.top_left_y, (TOTAL_COLS * cell_size), (TOTAL_ROWS * cell_size))

        # Draw the border rectangle
        pygame.draw.rect(self.screen, (255, 255, 255), border_rect, 1)
    
    def display_high_score(self):
        self.display_text(f"High Score", 1.15, 150)
        self.display_text(f"{self.high_score}", 1.15, 185)

    def display_score(self):
        self.display_text(f"Score: {self.board.score}", 1.3)

    def display_lines_cleared(self):
        self.display_text(f"Lines: {self.board.lines_cleared}", 4)
    
    def display_text(self, text_string, x_constant, y_constant=0):
        text = self.font.render(text_string, True, (255, 255, 255))
        text_rect = text.get_rect()
        text_rect.center = (screen_width // x_constant, 50 + y_constant)

        pygame.draw.rect(self.screen, (0, 0, 0), (text_rect.left, text_rect.top, text_rect.width, text_rect.height))

        self.screen.blit(text, text_rect)

    def display_level(self):
        self.display_text(f"Level: {self.board.level}", 2)

    def display_next_piece(self, piece):
        # Clear the area where the next piece will be displayed
        pygame.draw.rect(self.screen, (0, 0, 0), (NEXT_PIECE_X + 110, NEXT_PIECE_Y - 665, 200, 100))
        
        # Draw the next piece
        for idx, block in enumerate(piece.orientation):
            if block == '1':
                col_offset, row_offset = offsets[idx]
                spot = (piece.col + col_offset, piece.row + row_offset)
                pygame.draw.rect(self.screen, piece.color, (NEXT_PIECE_X + spot[0] * cell_size, NEXT_PIECE_Y + 75 - (spot[1] * cell_size), cell_size, cell_size))
