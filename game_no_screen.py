import pygame
from piece import Piece
from board import Board
import os
import sys

FPS = 60

RIGHT = 1
LEFT = -1
CLOCKWISE = 1
COUNTER_CLOCKWISE = -1

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
    def __init__(self, starting_level):
        pygame.init()
        self.first_level = starting_level
        self.running = True

        self.board = Board(self.first_level)

        self.curr_piece = Piece(-1)
        self.next_piece = Piece(self.curr_piece.letter_index)

        self.fall_time = 0

        self.clock = pygame.time.Clock()

        self.delay = 10
        self.cleared_lines = False

    def run(self, best_position=None):
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