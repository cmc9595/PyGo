#import sgfmill
#from sgfmill import boards
#from sgfmill import ascii_boards
import numpy as np
from copy import deepcopy
import sys
np.set_printoptions(threshold=sys.maxsize)

BLACK, WHITE, EMPTY = "#", "o", "."
stone = {"b":"#", "w":"o"}
enemy_stone = {"b":"o", "w":"#"}

class State(object):
    def __init__(self, board=None):
        if board is None:
            self.board = [["." for _ in range(19)]for _ in range(19)]
        else:
            self.board = board

        self.next_move = [-1, -1, '']
        self.move_num = 1 # move number 1~
        self.move_board = [[0 for _ in range(19)]for _ in range(19)]
        self.move_rec = []
        self.white_cap = 0 # 백 잡은돌
        self.black_cap = 0 # 흑 잡은돌
        self.prev_board = [["." for _ in range(19)]for _ in range(19)]
        self.prev_prev_board = [["." for _ in range(19)]for _ in range(19)]
    
    def get_next_move(self, row, col, next_color):
        self.next_move[0] = row
        self.next_move[1] = col
        self.next_move[2] = next_color

    def serialize(self, turn):  # SERIALIZE 19X19X12 one hot incoding
        bstate = np.zeros(19*19, np.uint64) #bug was uint16!
        i = 0
        for row in range(19):
            for col in range(19):

                stone = self.stone_color(row, col, turn)*(2**41)
                ts = self.binary_plane(min(8, self.move_board[row][col]//2))*(2**33)
                lb = self.binary_plane(min(8, self.liberties(row, col, turn)))*(2**25)
                cp = self.binary_plane(min(8, self.capture_size(row, col, turn)))*(2**17)
                sa = self.binary_plane(min(8, self.self_atari_size(row, col, turn)))*(2**9)
                la = self.binary_plane(min(8, self.liberties_after(row, col, turn)))*(2**1)
                #ladder_cap = 0  # 1
                #ladder_esc = 0  # 1
                sensible = self.sensible(row, col, turn)
                bstate[i] = stone + ts + lb + cp + sa + la + sensible
                i+=1

        bstate = bstate.reshape(19, 19)
        state = np.zeros((46, 19, 19), np.uint8)
        # 0-3 columns is me/oppo/empty 
        # 4-11 turns since
        state[0] = (bstate>>43)&1
        state[1] = (bstate>>42)&1
        state[2] = (bstate>>41)&1
        state[3] = 1  # constant plane
        state[4] = (bstate>>40)&1
        state[5] = (bstate>>39)&1
        state[6] = (bstate>>38)&1
        state[7] = (bstate>>37)&1
        state[8] = (bstate>>36)&1
        state[9] = (bstate>>35)&1
        state[10] = (bstate>>34)&1
        state[11] = (bstate>>33)&1
        state[12] = (bstate>>32)&1
        state[13] = (bstate>>31)&1
        state[14] = (bstate>>30)&1
        state[15] = (bstate>>29)&1
        state[16] = (bstate>>28)&1
        state[17] = (bstate>>27)&1
        state[18] = (bstate>>26)&1
        state[19] = (bstate>>25)&1
        state[20] = (bstate>>24)&1
        state[21] = (bstate>>23)&1
        state[22] = (bstate>>22)&1
        state[23] = (bstate>>21)&1
        state[24] = (bstate>>20)&1
        state[25] = (bstate>>19)&1
        state[26] = (bstate>>18)&1
        state[27] = (bstate>>17)&1
        state[28] = (bstate>>16)&1
        state[29] = (bstate>>15)&1
        state[30] = (bstate>>14)&1
        state[31] = (bstate>>13)&1
        state[32] = (bstate>>12)&1
        state[33] = (bstate>>11)&1
        state[34] = (bstate>>10)&1
        state[35] = (bstate>>9)&1
        state[36] = (bstate>>8)&1
        state[37] = (bstate>>7)&1
        state[38] = (bstate>>6)&1
        state[39] = (bstate>>5)&1
        state[40] = (bstate>>4)&1
        state[41] = (bstate>>3)&1
        state[42] = (bstate>>2)&1
        state[43] = (bstate>>1)&1
        state[44] = (bstate>>0)&1
        state[45] = 0  # constant plane
        return state

    def binary_plane(self, n):  # n=1~8
        ret=0
        for i in range(n):
            ret += 2**(7-i)
        return ret

    def stone_color(self, row, col, turn):
        if self.board[row][col] == stone[turn]: # mystone
            ret = 4
        elif self.board[row][col] == enemy_stone[turn]: # opponent stone
            ret = 2
        else: #empty space
            ret = 1
        return ret

    def liberties(self, row, col, turn): # 내 돌의 liberty계산
        if self.board[row][col] == ".": #empty
            return 0
        cluster = self.get_cluster(row, col, turn)
        if cluster==False:
            return 0
        border = self.get_cluster_border(cluster)
        cnt=0
        for (r, c) in border:
            if self.board[r][c] == ".":
                cnt+=1
        return cnt

    def capture_size(self, row, col, turn): # 상대 돌 몇개나 잡을건가
        if self.board[row][col] != ".":
            return 0
        cnt = 0
        ret = self.is_capturing_move(row, col, turn)
        for cluster in ret:
            for (r,c) in cluster:
                cnt += 1
        return cnt

    def self_atari_size(self, row, col, turn): # 여기 두면 몇개나 잡힐것인지
        if self.board[row][col] != ".":
            return 0
        cnt = 0
        ret = self.is_capturing_move(row, col, 'b' if turn=='w' else 'w')
        for cluster in ret:
            for (r, c) in cluster:
                cnt += 1
        return cnt

    def liberties_after(self, row, col, turn):
        # self.next_move[] = row, col, nextcolour
        self.board[self.next_move[0]][self.next_move[1]] = stone[self.next_move[2]]
        ret = self.liberties(row, col, turn)
        self.board[self.next_move[0]][self.next_move[1]] = EMPTY
        return ret
    
    def is_ladder_capture(self, row, col, turn): #상대 축으로 잡으면 true반환
        if self.board[row][col] != EMPTY:
            return 0
        ret = self.is_capturing_move(row, col, turn) # 상대 색깔 cluster 조사
        if ret==False:
            return 0
        pass
    def is_ladder_escape(self, row, col, turn): #내가 축으로 잡히면 true
        if self.board[row][col] != EMPTY:
            return 0
        ret = self.is_capturing_move(row, col, 'b' if turn=='w' else 'w')
        pass
    def sensible(self, row, col, turn): # have to consider whether it filles own eyes
        if self.is_playable(row, col, turn):
            return 1
        else:
            return 0
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
                     #print("capture:", r, c)
                    self.board[r][c] = "." #따낸 돌 들어내기
                    num += 1
        if color=='w':
            self.black_cap += num
        else:
            self.white_cap += num
            
        self.board[row][col] = stone[color]
        self.move_rec.append((self.move_num, row, col, color))
        self.move_board[row][col] = self.move_num
        self.move_num += 1
        return True
        
    def printboard(self):
        for i in range(19):
            print("%3d " % i, end='')
            for j in range(19):
                print(self.board[i][j], end=' ')
            print()
            if i==18:
                print("  ", end=' ')
        for k in range(19):
            print("%2d"%k, end='')
        print()

    def forhtml(self):
        ret = ""
        for i in range(19):
            for j in range(19):
                ret += self.board[i][j]
        return ret

    def printboard_with_pos(self, arr):
        for i in range(19):
            print("%3d " % i, end='')
            for j in range(19):
                if (i, j) in arr:
                    if self.board[i][j]==".":
                        print("x", end=' ')
                    else:
                        print("X", end=' ')
                else:
                    print(self.board[i][j], end=' ')
            print()
            if i==18:
                print("  ", end=' ')
        for k in range(19):
            print("%2d"%k, end='')
        print()

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

    s.play(3, 3, 'w')
    s.play(15, 15, 'w')
    s.play(3, 15, 'b')
    s.play(15, 3, 'b')
    s.play(3, 5, 'w')
    s.play(2, 15, 'w')
    s.play(2, 16, 'b')
    s.play(10, 3, 'w')
    s.play(2, 14, 'b')
    s.play(3, 3, 'w')
    s.play(3, 3, 'w')
    s.play(3, 3, 'w')
    s.play(3, 3, 'w')
    s.play(3, 3, 'w')
    s.play(3, 3, 'w')
    s.play(3, 3, 'w')
    s.play(3, 3, 'w')
    s.play(3, 3, 'w')
    s.play(3, 3, 'w')
    s.play(3, 3, 'w')
    s.play(3, 3, 'w')


#s.play(1, 1, 'b')

    printboard(s.board)
    s.next_move=[10, 10, 'w']
    print(s.serialize('w'))
    print(s.next_move)

    """
    print("liberties:")
    for i in range(19):
        for j in range(19):
            print(s.liberties(i, j,'w'), end=' ')
        print()


    print("capture:")
    for i in range(19):
        for j in range(19):
            print(s.capture_size(i, j,'w'), end=' ')
        print()
    print("self-atari:")
    for i in range(19):
        for j in range(19):
            print(s.self_atari_size(i, j,'w'), end=' ')
        print()
            """


