import sgfmill
from sgfmill import boards
from sgfmill import ascii_boards
import numpy as np

class State(object):
    def __init__(self, board=None):
        if board is None:
            self.board = boards.Board(19)
        else:
            self.board = board

    def serialize(self):  # SERIALIZE
        bstate = np.zeros(19*19, np.uint8)
        i = 0
        for row in range(19):
            for col in range(19):
                if self.board.get(row, col) == 'b':
                    bstate[i] = 4
                elif self.board.get(row, col) == 'w':
                    bstate[i] = 2
                else:  # None
                    bstate[i] = 1
                i+=1
        bstate = bstate.reshape(19, 19)

        state = np.zeros((4, 19, 19), np.uint8)

        # 0-3 columns is black/white/empty
        state[0] = (bstate>>2)&1
        state[1] = (bstate>>1)&1
        state[2] = (bstate>>0)&1
        state[3] = 1  # constant plane filled with 1
        return state


if __name__ == "__main__":
    s = State()
