import pygame
from random import randint
from enum import Enum

pygame.init()

clock = pygame.time.Clock()
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
LIGHT_BLUE = (21, 244, 238)
BLUE = (3, 65, 174)
ORANGE = (255, 151, 28)
YELLOW = (255, 213, 0)
LIGHT_GREEN = (114, 203, 59)
LIGHT_RED = (255, 50, 19)
PURPLE = (110, 3, 177)
colors = [BLACK, LIGHT_BLUE, BLUE, ORANGE, YELLOW, LIGHT_GREEN, LIGHT_RED, PURPLE]


class GameActions(Enum):
    NOTHING = 0
    START = 1
    END = 2
    PAUSE = 3
    UNPAUSE = 4
    PLAY = 5
    EXIT = 6


class Scenes(Enum):
    MAINMENU = 1
    HIGHSCORES = 2
    SETTINGS = 3
    PLAY = 4


class GameState(Enum):
    PAUSE = 1
    PLAY = 2


class Piece:

    def __init__(self, x, y, color, id):
        self.id = id
        self.x = x
        self.y = y
        self.color = color
        self.can_down = False
        self.on_ground = False

    def draw(self, grid, block_id):
        grid.grid[self.y][self.x] = block_id

    def move(self, direction):
        if direction == 0:
            self.x -= 1
        if direction == 1:
            self.x += 1


def move_piece(piece, center_pos, move_x, move_y):
    piece.x = center_pos[0] + move_x
    piece.y = center_pos[1] + move_y


class Block:
    id = 1

    def __init__(self):
        self.id = Block.id
        Block.id += 1
        self.pieces = [Piece(4, 0, 2, 1)]
        self.on_ground = False
        self.active = True
        self.can_left = True
        self.can_right = True
        self.can_down = True
        self.shape = None
        self.alignment = 0
        self.default_fall_time = 7
        self.fall_cool_down = 7
        self.move_cool_down = 1
        self.rotate_cool_down = 1
        self.center_pos = [0, 0]
        self.final_move_counter = 5
        self.user_input = get_user_input()
        self.grid = None
        self.block_added = False

    def update_block(self, drop_cool_down, grid):
        self.grid = grid
        self.user_input = get_user_input()
        self.check_boundaries()
        if not self.can_down and self.final_move_counter > 0:
            if self.user_input["left"] and self.can_left:
                for piece in self.pieces:
                    piece.move(0)
                self.final_move_counter = 0
                self.center_pos[0] -= 1
            elif self.user_input["right"] and self.can_right:
                for piece in self.pieces:
                    piece.move(1)
                    self.final_move_counter = 0
                self.center_pos[0] += 1
            self.final_move_counter -= 1
        if self.active:
            if self.user_input["space"] and drop_cool_down == 4:
                drop_cool_down = 0
                self.drop_down()
            if self.user_input["down"]:
                self.default_fall_time = 1
            else:
                self.default_fall_time = 5
            if self.user_input["up"]:
                if self.rotate_cool_down == 0:
                    self.check_boundaries()
                    if self.can_down:
                        self.rotate_cool_down = 1
                        self.rotate()
                else:
                    self.rotate_cool_down -= 1
            if self.move_cool_down == 0 and self.can_down:
                self.move_cool_down = 1
                if self.user_input["left"] and self.can_left:
                    if self.can_left:
                        for piece in self.pieces:
                            piece.move(0)
                        self.center_pos[0] -= 1
                elif self.user_input["right"] and self.can_right:
                    if self.can_right:
                        for piece in self.pieces:
                            piece.move(1)
                        self.center_pos[0] += 1
            else:
                self.move_cool_down -= 1
            if self.can_down and self.fall_cool_down == 0:
                self.fall_cool_down = self.default_fall_time
                for piece in self.pieces:
                    piece.y += 1
                self.center_pos[1] += 1
            else:
                self.fall_cool_down -= 1
        if not self.can_down and self.final_move_counter <= 0 and not self.block_added:
            self.block_added = True
            return [self.grid, drop_cool_down, True]
        else:
            return [self.grid, drop_cool_down, False]

    def rotate(self):
        pass

    def check_boundaries(self):
        for piece in self.pieces:
            if piece.x == 0:
                self.can_left = False
                break
            else:
                self.can_left = True
            if self.can_left:
                if self.grid.grid[piece.y][piece.x - 1] != 0 and self.grid.grid[piece.y][piece.x - 1] != self.id:
                    self.can_left = False
                    break
            else:
                self.can_left = True
        for piece in self.pieces:
            if piece.x == 9:
                self.can_right = False
                break
            else:
                self.can_right = True
            if self.grid.grid[piece.y][piece.x + 1] != 0 and self.grid.grid[piece.y][piece.x + 1] != self.id:
                self.can_right = False
                break
            else:
                self.can_right = True
        for piece in self.pieces:
            if piece.y == 23:
                self.can_down = False
                if self.active:
                    self.on_ground = True
                    self.active = False
                break
            else:
                self.can_down = True
            if not self.on_ground:
                if self.grid.grid[piece.y + 1][piece.x] != 0 and self.grid.grid[piece.y + 1][piece.x] != self.id:
                    self.can_down = False
                    if self.active:
                        self.active = False
                    break
                else:
                    self.can_down = True

    def drop_down(self):
        while self.can_down:
            self.check_boundaries()
            if self.can_down:
                for piece in self.pieces:
                    piece.y += 1
            else:
                break
            self.check_boundaries()


class L_block(Block):

    def __init__(self):
        super().__init__()
        self.color = 3
        self.alignments = 4
        self.center_pos = [4, 1]
        self.pieces = [Piece(3, 1, self.color, 1),
                       Piece(4, 1, self.color, 2),
                       Piece(5, 1, self.color, 3),
                       Piece(5, 0, self.color, 4)]

    def rotate(self):
        if not (self.alignment >= 0 and not self.can_down):
            if self.alignment + 1 > self.alignments:
                self.alignment = 0
            else:
                self.alignment += 1
        if self.alignment == 0:
            if not self.can_left and self.center_pos[0] == 0:
                self.center_pos[0] -= 1
            for piece in self.pieces:
                if piece.id == 1:
                    move_piece(piece, self.center_pos, -1, 0)
                elif piece.id == 2:
                    move_piece(piece, self.center_pos, 0, 0)
                elif piece.id == 3:
                    move_piece(piece, self.center_pos, 1, 0)
                elif piece.id == 4:
                    move_piece(piece, self.center_pos, 1, -1)
        elif self.alignment == 1:
            for piece in self.pieces:
                if piece.id == 1:
                    move_piece(piece, self.center_pos, 0, -1)
                elif piece.id == 2:
                    move_piece(piece, self.center_pos, 0, 0)
                elif piece.id == 3:
                    move_piece(piece, self.center_pos, 0, 1)
                elif piece.id == 4:
                    move_piece(piece, self.center_pos, 1, 1)
        elif self.alignment == 2:
            if not self.can_right and self.center_pos[0] == 9:
                self.center_pos[0] += 1
            for piece in self.pieces:
                if piece.id == 1:
                    move_piece(piece, self.center_pos, 1, 0)
                elif piece.id == 2:
                    move_piece(piece, self.center_pos, 0, 0)
                elif piece.id == 3:
                    move_piece(piece, self.center_pos, -1, 0)
                elif piece.id == 4:
                    move_piece(piece, self.center_pos, -1, 1)
        elif self.alignment == 3:
            for piece in self.pieces:
                if piece.id == 1:
                    move_piece(piece, self.center_pos, 0, 1)
                elif piece.id == 2:
                    move_piece(piece, self.center_pos, 0, 0)
                elif piece.id == 3:
                    move_piece(piece, self.center_pos, 0, -1)
                elif piece.id == 4:
                    move_piece(piece, self.center_pos, -1, -1)


class J_block(Block):

    def __init__(self):
        super().__init__()
        self.color = 2
        self.alignments = 4
        self.center_pos = [4, 1]
        self.pieces = [Piece(3, 0, self.color, 1),
                       Piece(3, 1, self.color, 2),
                       Piece(4, 1, self.color, 3),
                       Piece(5, 1, self.color, 4)]

    def rotate(self):
        self.check_boundaries()
        if not (self.alignment >= 0 and not self.can_down):
            if self.alignment + 1 > self.alignments:
                self.alignment = 0
            else:
                self.alignment += 1
        if self.alignment == 0:
            if not self.can_right and self.center_pos[0] == 9:
                self.center_pos[0] -= 1
            for piece in self.pieces:
                if piece.id == 1:
                    move_piece(piece, self.center_pos, -1, -1)
                elif piece.id == 2:
                    move_piece(piece, self.center_pos, -1, 0)
                elif piece.id == 3:
                    move_piece(piece, self.center_pos, 0, 0)
                elif piece.id == 4:
                    move_piece(piece, self.center_pos, 1, 0)
        elif self.alignment == 1:
            for piece in self.pieces:
                if piece.id == 1:
                    move_piece(piece, self.center_pos, 1, -1)
                elif piece.id == 2:
                    move_piece(piece, self.center_pos, 0, -1)
                elif piece.id == 3:
                    move_piece(piece, self.center_pos, 0, 0)
                elif piece.id == 4:
                    move_piece(piece, self.center_pos, 0, 1)
        elif self.alignment == 2:
            if not self.can_left and self.center_pos[0] == 0:
                self.center_pos[0] += 1
            for piece in self.pieces:
                if piece.id == 1:
                    move_piece(piece, self.center_pos, 1, 1)
                elif piece.id == 2:
                    move_piece(piece, self.center_pos, 1, 0)
                elif piece.id == 3:
                    move_piece(piece, self.center_pos, 0, 0)
                elif piece.id == 4:
                    move_piece(piece, self.center_pos, -1, 0)
        elif self.alignment == 3:
            if not self.can_left and self.center_pos[0] == 9:
                self.center_pos[0] += 1
            for piece in self.pieces:
                if piece.id == 1:
                    move_piece(piece, self.center_pos, -1, 1)
                elif piece.id == 2:
                    move_piece(piece, self.center_pos, 0, 1)
                elif piece.id == 3:
                    move_piece(piece, self.center_pos, 0, 0)
                elif piece.id == 4:
                    move_piece(piece, self.center_pos, 0, -1)


class I_block(Block):

    def __init__(self):
        super().__init__()
        self.color = 1
        self.alignments = 4
        self.center_pos = [4, 0]
        self.pieces = [Piece(3, 0, self.color, 1),
                       Piece(4, 0, self.color, 2),
                       Piece(5, 0, self.color, 3),
                       Piece(6, 0, self.color, 4)]

    def rotate(self):
        self.check_boundaries()
        if not (self.alignment >= 0 and not self.can_down):
            if self.alignment + 1 > self.alignments:
                self.alignment = 0
            else:
                self.alignment += 1
        if self.alignment == 0:
            self.center_pos[1] -= 1
            if not self.can_left and self.center_pos[0] == 0:
                self.center_pos[0] += 1
            elif not self.can_right and self.center_pos[0] == 9:
                self.center_pos[0] -= 2
            for piece in self.pieces:
                if piece.id == 1:
                    move_piece(piece, self.center_pos, -1, 0)
                elif piece.id == 2:
                    move_piece(piece, self.center_pos, 0, 0)
                elif piece.id == 3:
                    move_piece(piece, self.center_pos, 1, 0)
                elif piece.id == 4:
                    move_piece(piece, self.center_pos, 2, 0)
        elif self.alignment == 1:
            self.center_pos[0] += 1
            for piece in self.pieces:
                if piece.id == 1:
                    move_piece(piece, self.center_pos, 0, -1)
                elif piece.id == 2:
                    move_piece(piece, self.center_pos, 0, 0)
                elif piece.id == 3:
                    move_piece(piece, self.center_pos, 0, 1)
                elif piece.id == 4:
                    move_piece(piece, self.center_pos, 0, 2)
        elif self.alignment == 2:
            self.center_pos[1] += 1
            if not self.can_left and self.center_pos[0] == 0:
                self.center_pos[0] += 2
            elif not self.can_right and self.center_pos[0] == 9:
                self.center_pos[0] -= 1
            for piece in self.pieces:
                if piece.id == 1:
                    move_piece(piece, self.center_pos, 1, 0)
                elif piece.id == 2:
                    move_piece(piece, self.center_pos, 0, 0)
                elif piece.id == 3:
                    move_piece(piece, self.center_pos, -1, 0)
                elif piece.id == 4:
                    move_piece(piece, self.center_pos, -2, 0)
        elif self.alignment == 3:
            self.center_pos[0] -= 1
            for piece in self.pieces:
                if piece.id == 1:
                    move_piece(piece, self.center_pos, 0, 1)
                elif piece.id == 2:
                    move_piece(piece, self.center_pos, 0, 0)
                elif piece.id == 3:
                    move_piece(piece, self.center_pos, 0, -1)
                elif piece.id == 4:
                    move_piece(piece, self.center_pos, 0, -2)


class O_block(Block):

    def __init__(self):
        super().__init__()
        self.color = 4
        self.alignments = 0
        self.center_pos = [4, 0]
        self.pieces = [Piece(4, 0, self.color, 1),
                       Piece(4, 1, self.color, 2),
                       Piece(5, 0, self.color, 3),
                       Piece(5, 1, self.color, 4)]

    def rotate(self):
        pass


class S_block(Block):

    def __init__(self):
        super().__init__()
        self.color = 5
        self.alignments = 4
        self.center_pos = [4, 1]
        self.pieces = [Piece(3, 1, self.color, 1),
                       Piece(4, 1, self.color, 2),
                       Piece(4, 0, self.color, 3),
                       Piece(5, 0, self.color, 4)]

    def rotate(self):
        self.check_boundaries()
        if not (self.alignment >= 0 and not self.can_down):
            if self.alignment + 1 > self.alignments:
                self.alignment = 0
            else:
                self.alignment += 1
        if self.alignment == 0:
            if not self.can_left and self.center_pos[0] == 0:
                self.center_pos[0] += 1
            elif not self.can_right and self.center_pos[0] == 9:
                self.center_pos[0] -= 1
            for piece in self.pieces:
                if piece.id == 1:
                    move_piece(piece, self.center_pos, -1, 0)
                elif piece.id == 2:
                    move_piece(piece, self.center_pos, 0, 0)
                elif piece.id == 3:
                    move_piece(piece, self.center_pos, 0, -1)
                elif piece.id == 4:
                    move_piece(piece, self.center_pos, 1, -1)
        elif self.alignment == 1:
            for piece in self.pieces:
                if piece.id == 1:
                    move_piece(piece, self.center_pos, 0, -1)
                elif piece.id == 2:
                    move_piece(piece, self.center_pos, 0, 0)
                elif piece.id == 3:
                    move_piece(piece, self.center_pos, 1, 0)
                elif piece.id == 4:
                    move_piece(piece, self.center_pos, 1, 1)
        elif self.alignment == 2:
            if not self.can_left and self.center_pos[0] == 0:
                self.center_pos[0] += 1
            elif not self.can_right and self.center_pos[0] == 9:
                self.center_pos[0] -= 1
            for piece in self.pieces:
                if piece.id == 1:
                    move_piece(piece, self.center_pos, 1, 0)
                elif piece.id == 2:
                    move_piece(piece, self.center_pos, 0, 0)
                elif piece.id == 3:
                    move_piece(piece, self.center_pos, 0, 1)
                elif piece.id == 4:
                    move_piece(piece, self.center_pos, -1, 1)
        elif self.alignment == 3:
            for piece in self.pieces:
                if piece.id == 1:
                    move_piece(piece, self.center_pos, 0, 1)
                elif piece.id == 2:
                    move_piece(piece, self.center_pos, 0, 0)
                elif piece.id == 3:
                    move_piece(piece, self.center_pos, -1, 0)
                elif piece.id == 4:
                    move_piece(piece, self.center_pos, -1, -1)


class Z_block(Block):

    def __init__(self):
        super().__init__()
        self.color = 6
        self.alignments = 4
        self.center_pos = [4, 1]
        self.pieces = [Piece(3, 0, self.color, 1),
                       Piece(4, 0, self.color, 2),
                       Piece(4, 1, self.color, 3),
                       Piece(5, 1, self.color, 4)]

    def rotate(self):
        self.check_boundaries()
        if not (self.alignment >= 0 and not self.can_down):
            if self.alignment + 1 > self.alignments:
                self.alignment = 0
            else:
                self.alignment += 1
        if self.alignment == 0:
            if not self.can_left and self.center_pos[0] == 0:
                self.center_pos[0] += 1
            elif not self.can_right and self.center_pos[0] == 9:
                self.center_pos[0] -= 1
            for piece in self.pieces:
                if piece.id == 1:
                    move_piece(piece, self.center_pos, -1, -1)
                elif piece.id == 2:
                    move_piece(piece, self.center_pos, 0, -1)
                elif piece.id == 3:
                    move_piece(piece, self.center_pos, 0, 0)
                elif piece.id == 4:
                    move_piece(piece, self.center_pos, 1, 0)
        elif self.alignment == 1:
            for piece in self.pieces:
                if piece.id == 1:
                    move_piece(piece, self.center_pos, 1, -1)
                elif piece.id == 2:
                    move_piece(piece, self.center_pos, 1, 0)
                elif piece.id == 3:
                    move_piece(piece, self.center_pos, 0, 0)
                elif piece.id == 4:
                    move_piece(piece, self.center_pos, 0, 1)
        elif self.alignment == 2:
            if not self.can_left and self.center_pos[0] == 0:
                self.center_pos[0] += 1
            elif not self.can_right and self.center_pos[0] == 9:
                self.center_pos[0] -= 1
            for piece in self.pieces:
                if piece.id == 1:
                    move_piece(piece, self.center_pos, 1, 1)
                elif piece.id == 2:
                    move_piece(piece, self.center_pos, 0, 1)
                elif piece.id == 3:
                    move_piece(piece, self.center_pos, 0, 0)
                elif piece.id == 4:
                    move_piece(piece, self.center_pos, -1, 0)
        elif self.alignment == 3:
            for piece in self.pieces:
                if piece.id == 1:
                    move_piece(piece, self.center_pos, -1, 1)
                elif piece.id == 2:
                    move_piece(piece, self.center_pos, -1, 0)
                elif piece.id == 3:
                    move_piece(piece, self.center_pos, 0, 0)
                elif piece.id == 4:
                    move_piece(piece, self.center_pos, 0, -1)


class T_block(Block):

    def __init__(self):
        super().__init__()
        self.color = 7
        self.alignments = 4
        self.center_pos = [4, 1]
        self.pieces = [Piece(3, 1, self.color, 1),
                       Piece(4, 1, self.color, 2),
                       Piece(4, 0, self.color, 3),
                       Piece(5, 1, self.color, 4)]

    def rotate(self):
        self.check_boundaries()
        if not (self.alignment >= 0 and not self.can_down):
            if self.alignment + 1 > self.alignments:
                self.alignment = 0
            else:
                self.alignment += 1
        if self.alignment == 0:
            if not self.can_left and self.center_pos[0] == 0:
                self.center_pos[0] += 1
            elif not self.can_right and self.center_pos[0] == 9:
                self.center_pos[0] -= 1
            for piece in self.pieces:
                if piece.id == 1:
                    move_piece(piece, self.center_pos, -1, 0)
                elif piece.id == 2:
                    move_piece(piece, self.center_pos, 0, 0)
                elif piece.id == 3:
                    move_piece(piece, self.center_pos, 0, -1)
                elif piece.id == 4:
                    move_piece(piece, self.center_pos, 1, 0)
        elif self.alignment == 1:
            for piece in self.pieces:
                if piece.id == 1:
                    move_piece(piece, self.center_pos, 0, -1)
                elif piece.id == 2:
                    move_piece(piece, self.center_pos, 0, 0)
                elif piece.id == 3:
                    move_piece(piece, self.center_pos, 1, 0)
                elif piece.id == 4:
                    move_piece(piece, self.center_pos, 0, 1)
        elif self.alignment == 2:
            if not self.can_left and self.center_pos[0] == 0:
                self.center_pos[0] += 1
            elif not self.can_right and self.center_pos[0] == 9:
                self.center_pos[0] -= 1
            for piece in self.pieces:
                if piece.id == 1:
                    move_piece(piece, self.center_pos, 1, 0)
                elif piece.id == 2:
                    move_piece(piece, self.center_pos, 0, 0)
                elif piece.id == 3:
                    move_piece(piece, self.center_pos, 0, 1)
                elif piece.id == 4:
                    move_piece(piece, self.center_pos, -1, 0)
        elif self.alignment == 3:
            for piece in self.pieces:
                if piece.id == 1:
                    move_piece(piece, self.center_pos, 0, 1)
                elif piece.id == 2:
                    move_piece(piece, self.center_pos, 0, 0)
                elif piece.id == 3:
                    move_piece(piece, self.center_pos, -1, 0)
                elif piece.id == 4:
                    move_piece(piece, self.center_pos, 0, -1)


class Grid:

    def __init__(self, size, x, y, border_width, border_color):
        self.size = size
        self.rows = 20
        self.columns = 10
        self.x = x
        self.y = y
        self.border_width = border_width // 2
        self.border_color = border_color

        self.grid = [[0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                     [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                     [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                     [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                     [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                     [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                     [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                     [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                     [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                     [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                     [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                     [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                     [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                     [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                     [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                     [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                     [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                     [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                     [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                     [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                     [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                     [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                     [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                     [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]]

    def draw(self, surface, blocks):
        for row in range(4, self.rows + 4):
            pos_y = self.y + (self.size * row)
            for column in range(0, self.columns):
                square_color = None
                for block in blocks:
                    if block.id == self.grid[row][column]:
                        square_color = colors[block.color]
                        break
                    else:
                        square_color = colors[0]
                pos_x = self.x + (self.size * column)
                pygame.draw.rect(surface, self.border_color, ((pos_x, pos_y), (self.size, self.size)),
                                 self.border_width)
                pygame.draw.rect(surface, square_color, ((pos_x + self.border_width, pos_y + self.border_width), (
                    self.size - self.border_width * 2, self.size - self.border_width * 2)))

    def check_for_full_lines(self, blocks, score):
        full_rows = []
        blank_row = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        for row in range(4, self.rows + 4):
            spaces_full = 0
            for column in range(0, self.columns):
                if self.grid[row][column] != 0:
                    spaces_full += 1
            if spaces_full == 10:
                full_rows.append(row)
        for row in full_rows:
            score += 1
            for block in blocks:
                block.check_boundaries()
                pieces_removed = []
                pieces_to_remove = []
                for piece in block.pieces:
                    print(piece.y, piece.id)
                for piece in block.pieces:
                    if piece.y == row:
                        pieces_removed.append([piece.id, piece.y])
                        pieces_to_remove.append(piece.id)
                for id in pieces_to_remove:
                    for piece in block.pieces:
                        if piece.id == id:
                            block.pieces.remove(piece)
                for piece in pieces_removed:
                    print("id:", piece[0])
                    print("y:", piece[1], "\n")
                for piece in block.pieces:
                    print(piece.y, piece.id)
                print(len(block.pieces))
        for row in full_rows:
            self.grid[row] = blank_row
            for block in blocks:
                for piece in block.pieces:
                    if piece.y < row:
                        piece.y += 1
        return score

    def print_grid(self):
        for row in range(3, self.rows + 3):
            for column in range(0, 10):
                print(self.grid[row][column], end="")
            print("")

    def refresh_grid(self):
        self.grid = [[0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                     [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                     [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                     [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                     [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                     [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                     [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                     [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                     [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                     [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                     [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                     [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                     [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                     [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                     [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                     [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                     [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                     [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                     [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                     [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                     [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                     [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                     [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                     [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]]


class Text:

    def __init__(self, text, font_name, font_size, text_color, bg_color, x, y):
        self.text = text
        self.font = pygame.font.Font(font_name, font_size)
        self.font_size = font_size
        self.text_color = text_color
        self.bg_color = bg_color
        self.text_width, self.text_height = self.font.size(self.text)
        self.center = (self.text_width // 2, self.text_height // 2)
        self.x = x
        self.y = y

    def draw(self, surface, width=0, height=0):
        text = self.font.render(self.text, True, self.text_color, self.bg_color)
        surface.blit(text, (self.x - self.center[0] + width, self.y - self.center[1] + height))

    def change_text(self, text):
        self.text = text


class Text_Box:

    def __init__(self, x, y, width, height, text, font_size):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.center = [self.x - (self.width // 2), self.y - (self.height // 2)]
        self.text_pos = self.center
        self.text = text
        self.font_size = font_size
        self.text_obj = Text(self.text, "freesansbold.ttf", self.font_size, WHITE, BLACK, self.center[0],
                             self.center[1])

    def draw(self, surface, text=None):
        if text is not None:
            self.text_obj.change_text(text)
        pygame.draw.rect(surface, WHITE, (self.center, (self.width, self.height)), 5)
        self.text_obj.draw(surface, (self.width // 2), (self.height // 2))


class Text_Button(Text_Box):

    def __init__(self, x, y, width, height, text, font_size, action):
        super().__init__(x, y, width, height, text, font_size)
        self.action = action
        self.hover = False
        self.clicks = 0
        self.mouse_x = pygame.mouse.get_pos()[0]
        self.mouse_y = pygame.mouse.get_pos()[1]
        self.mouse_down = False

    def draw(self, surface, text=None):
        if text is not None:
            self.text_obj.change_text(text)
        if self.hover:
            pygame.draw.rect(surface, YELLOW, (self.center, (self.width, self.height)), 5)
        else:
            pygame.draw.rect(surface, WHITE, (self.center, (self.width, self.height)), 5)
        self.text_obj.draw(surface, (self.width // 2), (self.height // 2))
        if self.mouse_down and self.hover:
            self.clicks += 1
            return self.action
        else:
            return

    def get_mouse_data(self, mouse_down):
        self.mouse_down = mouse_down
        self.mouse_x = pygame.mouse.get_pos()[0]
        self.mouse_y = pygame.mouse.get_pos()[1]
        if self.center[0] <= self.mouse_x <= self.center[0] + self.width and self.center[1] <= self.mouse_y <= \
                self.center[1] + self.height:
            self.hover = True
        else:
            self.hover = False


class Image:

    def __init__(self, x, y, width, height, image_path):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.image = pygame.image.load(image_path)
        self.center = [self.x - (self.width // 2), self.y - (self.height // 2)]

    def draw(self, surface):
        surface.blit(self.image, self.center)


class Image_Button(Image):

    def __init__(self, x, y, width, height, image_path, action):
        super().__init__(x, y, width, height, image_path)
        self.action = action
        self.hover = False
        self.clicks = 0
        self.mouse_x = pygame.mouse.get_pos()[0]
        self.mouse_y = pygame.mouse.get_pos()[1]
        self.mouse_down = False

    def draw(self, surface):
        surface.blit(self.image, self.center)
        if self.mouse_down and self.hover:
            print("click")
            return self.action
        else:
            return

    def get_data(self, mouse_down):
        self.mouse_down = mouse_down
        self.mouse_x = pygame.mouse.get_pos()[0]
        self.mouse_y = pygame.mouse.get_pos()[1]
        if self.center[0] <= self.mouse_x <= self.center[0] + self.width and self.center[1] <= self.mouse_y <= \
                self.center[1] + self.height:
            self.hover = True
        else:
            self.hover = False


class Logo:

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = 200
        self.height = 100
        self.center = [(self.width // 2), (self.height // 2)]
        self.text = Text("TETRIS", "freesansbold.ttf", 50, BLUE, BLACK, self.x, self.y)

    def draw(self, surface):
        pygame.draw.rect(surface, WHITE, ((self.x - self.center[0], self.y - self.center[1]), (self.width, self.height)), 3)
        self.text.draw(surface)


class MainMenu:

    def __init__(self):
        self.start_button = Text_Button(250, 300, 200, 100, "PLAY", 30, GameActions.START)
        self.action = 0
        self.logo = Logo(250, 150)

    def main_loop(self, surface, mouse_down):
        self.logo.draw(surface)
        self.start_button.get_mouse_data(mouse_down)
        self.action = self.start_button.draw(surface)
        return self.action


class PauseMenu:

    def __init__(self, x, y, width, height):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.action = None
        self.center = [(self.width // 2), (self.height // 2)]
        self.resume_button = Text_Button(250, 300, 200, 100, "RESUME", 20, GameActions.UNPAUSE)
        self.quit_button = Text_Button(250, 500, 200, 100, "EXIT", 20, GameActions.EXIT)

    def draw(self, surface, mouse_down):
        pygame.draw.rect(surface, WHITE,
                         ((self.x - self.center[0], self.y - self.center[1]), (self.width, self.height)))
        pygame.draw.rect(surface, BLACK, (
            (self.x - self.center[0] + 5, self.y - self.center[1] + 5), (self.width - 10, self.height - 10)))
        self.resume_button.get_mouse_data(mouse_down)
        self.quit_button.get_mouse_data(mouse_down)
        self.action = self.quit_button.draw(surface)
        if self.action is None:
            self.action = self.resume_button.draw(surface)
        return self.action


class Game:

    def __init__(self):
        self.state = GameActions.PLAY
        self.running = True
        self.lost = False
        self.blocks = []
        self.drop_cool_down = 4
        self.default_fall_time = 5
        self.fall_cool_down = 5
        self.score = 0
        self.score_text = "score: " + str(self.score)
        self.score_pane = Text_Box(75, 50, 100, 50, self.score_text, 20)
        self.pause_button = Text_Button(475, 25, 20, 20, "||", 10, GameActions.PAUSE)
        self.pause_menu = PauseMenu(250, 400, 400, 700)
        self.grid = Grid(25, 125, 200, 2, WHITE)
        self.paused = False
        self.action = None
        self.can_add_block = False

    def main_loop(self, surface, mouse_down):
        pygame.time.delay(40)
        if self.action == GameActions.PAUSE:
            self.paused = True
            self.action = None
        elif self.action == GameActions.UNPAUSE:
            self.paused = False
            self.action = None
        if len(self.blocks) == 0:
            self.add_block()
        self.score_text = "score: " + str(self.score)
        self.pause_button.get_mouse_data(mouse_down)
        self.action = self.pause_button.draw(surface)
        self.score_pane.draw(surface, self.score_text)
        if self.drop_cool_down < 4 and not self.paused:
            self.drop_cool_down += 1
        for block in self.blocks:
            if not self.paused:
                self.grid, self.drop_cool_down, self.can_add_block = block.update_block(self.drop_cool_down, self.grid)
            if not block.active and block.final_move_counter <= 0:
                for piece in block.pieces:
                    if piece.y < 4:
                        print("lost")
                        self.lost = True
            for piece in block.pieces:
                piece.draw(self.grid, block.id)
        if self.can_add_block:
            self.add_block()
            self.can_add_block = False
        self.grid.draw(surface, self.blocks)
        if self.paused:
            self.action = self.pause_menu.draw(surface, mouse_down)
            if self.action == GameActions.EXIT:
                self.paused = False
        self.score = self.grid.check_for_full_lines(self.blocks, self.score)
        self.grid.refresh_grid()
        return self.action

    def add_block(self):
        print(len(self.blocks))
        block = randint(1, 7)
        if block == 1:
            self.blocks.append(I_block())
        elif block == 2:
            self.blocks.append(J_block())
        elif block == 3:
            self.blocks.append(L_block())
        elif block == 4:
            self.blocks.append(O_block())
        elif block == 5:
            self.blocks.append(S_block())
        elif block == 6:
            self.blocks.append(Z_block())
        elif block == 7:
            self.blocks.append(T_block())


def get_user_input():
    keys = {
        "left": False,
        "right": False,
        "down": False,
        "up": False,
        "space": False,
        "mouse_down": False
    }
    for event in pygame.event.get():
        if event.type == pygame.MOUSEBUTTONDOWN:
            keys["mouse_down"] = True
    keys_pressed = pygame.key.get_pressed()
    if keys_pressed[pygame.K_LEFT]:
        keys["left"] = True
    elif keys_pressed[pygame.K_RIGHT]:
        keys["right"] = True
    elif keys_pressed[pygame.K_DOWN]:
        keys["down"] = True
    elif keys_pressed[pygame.K_UP]:
        keys["up"] = True
    elif keys_pressed[pygame.K_SPACE]:
        keys["space"] = True
    return keys


def main():
    running = True
    scene = Scenes.MAINMENU
    screen = pygame.display.set_mode((500, 800))
    pygame.display.set_caption("Tetris")
    game = Game()
    mainmenu = MainMenu()
    action = None
    mouse_down = False
    while running:
        clock.tick(30)
        screen.fill(BLACK)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_down = True
        if scene == Scenes.MAINMENU:
            action = mainmenu.main_loop(screen, mouse_down)
            if action == GameActions.START:
                scene = Scenes.PLAY
                mainmenu = None
                game = Game()
                action = None
        elif scene == Scenes.PLAY:
            action = game.main_loop(screen, mouse_down)
            if action == GameActions.EXIT:
                scene = Scenes.MAINMENU
                mainmenu = MainMenu()
                game = None
                action = None
        mouse_down = False
        pygame.display.flip()


main()