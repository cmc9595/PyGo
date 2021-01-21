from sgfmill import sgf
from sgfmill import boards
from sgfmill import ascii_boards
import sys
import numpy as np
from state import State
from net import Net
import torch

class Valuator(object):
    def __init__(self):
        import torch
        vals = torch.load("SL.pth", map_location=torch.device('cpu'))
        self.model = Net()
        self.model.load_state_dict(vals)
    
    def __call__(self, s):
        current_board = s.serialize()[None]
        output = self.model(torch.tensor(current_board).float())
        return output

s = State() # board생성
v = Valuator()


np.set_printoptions(threshold=sys.maxsize, precision=3)

s.board.play(3, 15,'b')
s.board.play(3, 3,'w')
s.board.play(15, 3,'b')
s.board.play(16, 15,'w')
s.board.play(9, 2,'b')
s.board.play(14,16, 'w')
s.board.play(15,13,'b')
s.board.play(5, 16,'w')
s.board.play(2,13,'b')
s.board.play(2,5,'w')
s.board.play(5,2,'b')
s.board.play(2,16,'w')
s.board.play(3, 16, 'b')
s.board.play(3, 17, 'w')
s.board.play(2, 17, 'b')
s.board.play(16, 3, 'w')
s.board.play(14, 2, 'b')
s.board.play(15, 2, 'w')
s.board.play(16, 4, 'b')
s.board.play(15, 4, 'w')
s.board.play(16, 5, 'b')
s.board.play(14, 3, 'w')
s.board.play(15, 5, 'b')


print(ascii_boards.render_board(s.board))

out = v(s)
#out = out.squeeze()
print(out.size())
#out[0][0] = 0.111
out = out.reshape(19, 19)
l = []
for idx, i in enumerate(out):
    for idy, j in enumerate(i):
        if j==max(i):
            l.append([float(j), idx, idy])

l = sorted(l, reverse=True)
for i in range(5):
	print("%3d %3d  :  %.4f" % (l[i][1], l[i][2], l[i][0]))
