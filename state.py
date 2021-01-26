#import sgfmill
#from sgfmill import boards
#from sgfmill import ascii_boards
import numpy as np
from copy import deepcopy

stone = {"b":"#", "w":"o"}
enemy_stone = {"b":"o", "w":"#"}

class State(object):
    def __init__(self, board=None):
        if board is None:
            self.board = [["." for _ in range(19)]for _ in range(19)]
        else:
            self.board = board

        self.move_num = 1 # move number 1~
        self.move_rec = []
        self.white_cap = 0 # 백 잡은돌
        self.black_cap = 0 # 흑 잡은돌
        self.prev_board = [["." for _ in range(19)]for _ in range(19)]
        self.prev_prev_board = [["." for _ in range(19)]for _ in range(19)]

    def serialize(self):  # SERIALIZE
        bstate = np.zeros(19*19, np.uint8)
        i = 0
        for row in range(19):
            for col in range(19):
                if self.board[row][col] == '#':
                    bstate[i] = 4
                elif self.board[row][col] == 'o':
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

    def dfs(self, row, col, color, v):
        v[row][col] = 1
        for [r, c] in [[row+1, col], [row-1, col], [row, col+1], [row, col-1]]:
            if 0<=r<=18 and 0<=c<=18 and v[r][c]==0 and self.board[r][c]==stone[color]:
                self.dfs(r, c, color, v)
    def get_cluster(self, row, col, color):
        v = [[0 for _ in range(19)]for _ in range(19)]
        l = []
        if self.board[row][col] != stone[color]: #check empty/wrong color
            return False
        self.dfs(row, col, color, v) # v is cluster map

        for idx, i in enumerate(v):
            for jdx, j in enumerate(i):
                if j==1:
                    l.append((idx, jdx))
        return l
    def get_cluster_border(self, cluster):
        v = [[0 for _ in range(19)]for _ in range(19)]
        l = []
        if cluster is None:
            return False
        for (row, col) in cluster:
            if row+1<=18:l.append((row+1, col)) 
            if row-1>=0: l.append((row-1, col)) 
            if col+1<=18:l.append((row, col+1)) 
            if col-1>=0: l.append((row, col-1)) 
        l = list(set(l)-set(cluster))
        return l

    def is_capturing_move(self, row, col, color):
        if self.board[row][col] != ".": # check empty
            return False
        l = []
        for [r, c] in [[row+1, col], [row-1, col], [row, col+1], [row, col-1]]:
            if 0<=r<=18 and 0<=c<=18 and self.board[r][c]==enemy_stone[color]:
                cluster = self.get_cluster(r, c, 'b' if color=='w' else 'w')
                border = self.get_cluster_border(cluster)
                f = True
                for (r, c) in set(border)-set([(row,col)]):
                    if self.board[r][c] != stone[color]:
                        f = False
                        break
                if f==True: #둘러쌓인다면
                    l.append(tuple(cluster))
        return list(set(l)) if l is not None else False

    def is_suicide_move(self, row, col, color):
        if self.board[row][col] != ".": # check empty
            return False
        self.board[row][col] = stone[color]
        cluster = self.get_cluster(row, col, color)
        self.board[row][col] = "."

        for (r, c) in self.get_cluster_border(cluster):
            if self.board[r][c] != enemy_stone[color]:
                return False
        return True

    def is_playable(self, row, col, color):
        if self.board[row][col] != ".": # check empty
            return False
        if self.is_suicide_move(row, col, color):
            if self.is_capturing_move(row, col, color): 

                tmp = deepcopy(self.board)
                for cluster in self.is_capturing_move(row, col, color):
                    for (r, c) in cluster:
                        #print(r, c)
                        self.board[r][c] = "." #따낸 돌 들어내기
                self.board[row][col] = stone[color] #놓으면 따낸 상태이다.

                if self.prev_board == self.board: #Ko인 상태이므로 not playable.
                    self.board = deepcopy(tmp) #원위치
                    return False
                else:
                    self.board = deepcopy(tmp) #원위치
                    return True
            else:
                return False

        if not self.is_suicide_move(row, col, color):
            return True
    
    def play(self, row, col, color):
        if not self.is_playable(row, col, color):
            print("Not Playable at (%d, %d)" % (row, col))
            return False

        if self.move_num >= 3:
            self.prev_prev_board = deepcopy(self.prev_board)
        if self.move_num >= 2:
            self.prev_board = deepcopy(self.board)

        # handle capturing
        num = 0
        if self.is_capturing_move(row, col, color): #따낸 돌 제거먼저 하고 돌놔야 bug방지
            for cluster in self.is_capturing_move(row, col, color):
                for (r, c) in cluster:
                    self.board[r][c] = "." #따낸 돌 들어내기
                    num += 1
        if color=='w':
            self.black_cap += num
        else:
            self.white_cap += num
            
        self.board[row][col] = stone[color]
        self.move_rec.append((self.move_num, row, col, color))
        self.move_num += 1
        return True

def printboard(arr):
    for i in range(19):
        print("%3d " % i, end='')
        for j in range(19):
            print(arr[i][j], end=' ')
        print()
        if i==18:
            print("  ", end=' ')
    for k in range(19):
        print("%2d"%k, end='')
    print()

if __name__ == "__main__":
    s = State()
    s.play(0, 1, 'w')
    s.play(1, 0, 'w')
    s.play(1, 2, 'w')
    s.play(2, 1, 'w')

    s.play(2, 0, 'b')
    s.play(2, 2, 'b')
    s.play(3, 1, 'b')
    s.play(1, 1, 'b')

    s.play(5, 5, 'w')
    s.play(5, 6, 'b')

    s.play(2, 1, 'w')
    s.play(10, 10, 'b')
    s.play(10, 11, 'w')
    s.play(1, 1, 'b')
    s.play(0, 0, 'w')
    s.play(0, 2, 'b')
    s.play(0, 0, 'b')

#s.play(1, 1, 'b')

    printboard(s.board)
    printboard(s.prev_board)
    printboard(s.prev_prev_board)


#print(s.move_rec)


#s.printboard()

    #print(c)
    #print(s.get_cluster_border(c))

    #print(c1)
    #print(s.get_cluster_border(c1))
    
    """
    for r in range(19):
        for c in range(19):
            if s.is_capturing_move(r, c, 'w'):
                print("capturing: ", r, c, 'w')
                print(s.is_capturing_move(r, c, 'w'))
            if s.is_capturing_move(r, c, 'b'):
                print("capturing: ", r, c, 'b')
                print(s.is_capturing_move(r, c, 'b'))

            if s.is_suicide_move(r, c, 'w'):
                print("suicide: ", r, c, 'w')
            if s.is_suicide_move(r, c, 'b'):
                print("suicide: ", r, c, 'b')
    """
