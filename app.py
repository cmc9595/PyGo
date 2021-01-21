from flask import Flask, Response, request
app = Flask(__name__)
from state import State
from net import Net
import torch
import sys
import numpy as np
from sgfmill import ascii_boards

#from sgfmill import ascii_boards

class PolicyNet(object):
	def __init__(self):
		val = torch.load("SL2.pth", map_location=torch.device("cpu"))
		self.model = Net()
		self.model.load_state_dict(val)

	def __call__(self, s):
		b = s.serialize()[None] # food for thought
		output = self.model(torch.tensor(b).float())
		return output.float()

def getRowCol(tensor):
	# assume board size 19x19
	board_size = 19
	# change to nparray
	tensor = tensor.detach().numpy()
	tensor = tensor.reshape(19, 19)

	l=[]
	for row, i in enumerate(tensor):
		for col, j in enumerate(i):
			l.append([row, col, j])
	l = sorted(l, reverse=True, key = lambda x : x[2])
	return l

def ascii_to_graphic(s): # s.board를 그린다.
	pass


def computer_move(s, model):
	move = getRowCol(model(s))
	
	row = move[0][0]
	col = move[0][1]




s = State()
#s.board.play(row, col, colour)
s.board.play(3, 3, 'b')
model = PolicyNet()
#print(model(s))

ret = getRowCol(model(s))
for i in ret:
	print(i)

print(ascii_boards.render_board(s.board))
game = ascii_boards.interpret_diagram(ascii_boards.render_board(s.board), 19)
print(game)


@app.route("/")
def hello():
	'''
	ret = '<html><head><title>My Page</title>'
	ret += '<script src="https://ajax.googleapis.com/ajax/libs/jquery/3.5.1/jquery.min.js"></script>'
	ret += '</head><body>'

	ret += '<div id="board">'

	ret += '<form action="/move" method="get">'
	ret += '<input name="move" type="text"></input>'
	ret += '<input type="submit" value="Move"></input>'
	ret += '</form>'

	ret += '</body></html>'
	'''
	ret = open("index.html").read()
	print(ret)
	return ret

@app.route("/move")
def move():
	move = request.args.get("move", default="")
	print(move)

	return hello()



























if __name__ == "__main__":
	app.run(host='0.0.0.0', port='5000', debug=True)
