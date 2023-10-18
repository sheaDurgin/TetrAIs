level_delay = {
    0: 10, 1: 20, 2: 30, 3: 40, 4: 50, 5: 60, 6: 70, 7: 80, 8: 90,
    9: 100, 10: 100, 11: 100, 12: 100, 13: 100, 14: 100, 15: 100,
    16: 110, 17: 120, 18: 130, 19: 140, 20: 150, 21: 160, 22: 170, 23: 180, 24: 190,
    25: 200, 26: 200, 27: 200, 28: 200, 29: 200
}

score_per_line_cleared = [40, 100, 300, 1200, 0]

TOTAL_ROWS = 20
TOTAL_COLS = 10

def get_frames_index(level):
    if level >= 29:
        return 29
    elif level >= 19:
        return 19
    elif level >= 16:
        return 16
    elif level >= 13:
        return 13
    elif level >= 10:
        return 10
    return level

class Board:
    def __init__(self, level):
        self.blocks = {(col, row): (0, 0, 0) for col in range(10) for row in range(20)}
        self.score = 0
        self.level = level
        self.lines_cleared = 0
        self.lines_until_level_change = level_delay[self.level]
        self.frames_index = get_frames_index(self.level)

    def get_height_of_each_column(self):
        return [max([row for row in range(TOTAL_ROWS) if self.blocks[(col, row)] != (0, 0, 0)], default=0) 
                      for col in range(TOTAL_COLS)]

    # Returns absolute value of current bumpiness, whether or not we have a double well and the max height of the board
    def get_bumpiness(self):
        bumpy_list = self.get_height_of_each_column()

        prev_height = None
        bumpiness = 0
        for height in bumpy_list:
            if not prev_height:
                prev_height = height
            else:
                bumpiness += height - prev_height

            prev_height = height

        prev_height = min(bumpy_list[:-2])

        max_height = max(bumpy_list)

        return abs(bumpiness), max_height

    def get_line_dependencies(self):
        def calculate_line_dependencies(cnt):
            line_dependencies = 0
            if cnt >= 3:
                line_dependencies += 1
                cnt -= 3
                if cnt >= 4:
                    line_dependencies += cnt // 4
            cnt = 0
            return line_dependencies
                
        line_dependencies = 0
        prev_cells = [(1, 1, 1) for _ in range(TOTAL_ROWS)]
        for col in range(TOTAL_COLS):
            cnt = 0
            for row in range(TOTAL_ROWS):
                color = self.blocks[(col, row)]
                if color == (0, 0, 0) and prev_cells[row] != (0, 0, 0):
                    if col < TOTAL_COLS - 1 and self.blocks[(col+1, row)] != (0, 0, 0):
                        cnt += 1
                    elif col == TOTAL_COLS - 1:
                        cnt += 1
                else:
                    line_dependencies += calculate_line_dependencies(cnt)
                prev_cells[row] = color

            line_dependencies += calculate_line_dependencies(cnt)

        return line_dependencies
    
    def get_holes(self):
        holes = 0
        for col in range(TOTAL_COLS):
            empty_cells = 0
            for row in range(TOTAL_ROWS):
                if self.blocks[(col, row)] != (0, 0, 0):
                    holes += empty_cells
                    empty_cells = 0
                else:
                    empty_cells += 1
                    
        return holes
        
    def clear_lines(self):
        rows_cleared = [False for _ in range(TOTAL_ROWS)]
        for row in range(TOTAL_ROWS):
            clear = True
            for col in range(TOTAL_COLS):
                if self.blocks[(col, row)] == (0, 0, 0):
                    clear = False
                    break

            rows_cleared[row] = clear
        
        # Move lines down
        offset = 0
        for row in range(TOTAL_ROWS):
            if rows_cleared[row]:
                offset += 1
                continue
            elif offset == 0:
                continue

            for col in range(TOTAL_COLS):
                self.blocks[(col, row - offset)] = self.blocks[(col, row)]
                self.blocks[(col, row)] = (0, 0, 0)
        
        return offset
    
    def calculate_points(self, lines_cleared):
        self.lines_cleared += lines_cleared

        if self.lines_until_level_change <= self.lines_cleared:
            self.lines_until_level_change += 10
            self.level += 1
            self.frames_index = get_frames_index(self.level)

        return score_per_line_cleared[lines_cleared - 1] * (self.level + 1)