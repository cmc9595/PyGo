from state import State
from tqdm import tqdm
import os
from sgfmill import sgf
import numpy as np
import time
import sys
import traceback
np.set_printoptions(threshold=sys.maxsize)

filelist = []

with open("test.txt", "r") as f:
    while True:
        line = f.readline()
        if not line:break
        filelist.append(line)

X, Y = [], []

#print(os.listdir("test"))
ha=0
n=0
for x in tqdm(range(700, 1000), miniters=1):
    with open(filelist[x][6:28], "rb") as g:
        try:
            game = sgf.Sgf_game.from_bytes(g.read())
        except:
            continue

        if game.get_root().find("HA"):
            ha += 1
            continue

        s = State()
        
         #print("Game %d"%x)
        for i, move in enumerate(game.get_main_sequence()):

            try:
                color, m = move.get_move()
            except:
                break
             #print(i, color, move)
            if color is None or m is None: #None시탈출
                n+=1
                continue
            
            if i == len(game.get_main_sequence())-1: #last node시 탈출
                break

            try:
                next_color, next_move = game.get_main_sequence()[i + 1].get_move()
            except:
                break
            if next_color is None or next_move is None: #next node못읽어도 탈출
                break
            
            try:
                if s.play(m[0], m[1], color):
                    s.get_next_move(next_move[0], next_move[1], next_color)

                    #s.printboard()
                    #print(move, color)
                    X.append(s.serialize(color))
                    out = np.zeros((19, 19), np.uint8)
                    out[next_move[0]][next_move[1]] = 1
                    out = out.reshape(-1)
                    Y.append(out)
                else:
                    continue
            except Exception:
                traceback.print_exc()
                continue
            

X = np.array(X)
Y = np.array(Y)

#np.savez("test1000.npz", X, Y)

print(ha)
print(n)

print(X[-1])
print(Y[-1])


