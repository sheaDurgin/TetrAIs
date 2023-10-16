from board import Board
import numpy as np
from collections import deque
import random
from model import Linear_QNet, QTrainer
import torch

MAX_MEMORY = 100000
BATCH_SIZE = 1000
LR = 0.001

class Agent():
    def __init__(self):
        self.n_games = 0
        self.epsilon = 0 # randomness
        self.gamma = 0.9 # discount rate
        self.memory = deque(maxlen=MAX_MEMORY) # popleft()
        self.model = Linear_QNet(14, 256, 5)
        self.trainer = QTrainer(self.model, lr=LR, gamma=self.gamma)

    def get_state(self, game):
        state = []
        heights = game.board.get_height_of_each_column()
        # Heights for each column, left to right, 0 - 9
        state.extend(heights)
        # Current pieces position on the board along with its rotation, 10 - 12
        state.extend([game.curr_piece.col, game.curr_piece.row, game.curr_piece.orientation])
        # Next Pieces shape, 13
        state.append(game.next_piece.orientation)
        return np.array(state, dtype=int) # size of 14

    def remember(self, state, action, reward, next_state, done):
        self.memory.append((state, action, reward, next_state, done)) # popleft if MAX_MEMORY is reached

    def train_long_memory(self):
        if len(self.memory) > BATCH_SIZE:
            mini_sample = random.sample(self.memory, BATCH_SIZE) # list of tuples
        else:
            mini_sample = self.memory

        states, actions, rewards, next_states, dones = zip(*mini_sample)
        self.trainer.train_step(states, actions, rewards, next_states, dones)

    def train_short_memory(self, state, action, reward, next_state, done):
        self.trainer.train_step(state, action, reward, next_state, done)

    def get_action(self, state):
        # random moves: tradeoff exploration / exploitation
        self.epsilon = 80 - self.n_games
        final_move = [0, 0, 0, 0, 0]
        if random.randint(0, 200) < self.epsilon:
            move = random.randint(0, 4)
            final_move[move] = 1
        else:
            state0 = torch.tensor(state, dtype=torch.float)
            prediction = self.model(state0)
            move = torch.argmax(prediction).item()
            final_move[move] = 1

        return final_move