from flask import Flask, Response, request
import requests
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
		val = torch.load("SL3_5layer.pth", map_location=torch.device("cpu"))
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


s = State()
model = PolicyNet()

white_row="-1"
white_col="-1"

#url = 'http://13.125.243.134:5000/white'
#data = {'row': white_row, 'col': white_col}
#response = requests.get(url=url, params=data)
#print(response)

@app.route("/")
def hello():
	ret = open("index.html").read()
	return ret

@app.route("/move")
def move():
	row = 18 - int(request.args["row"])
	col = int(request.args["col"])
	#print("move: ", row, col)

	# human play
	s.board.play(row, col, 'b')

	# computer play
	out = getRowCol(model(s))
	s.board.play(out[0][0], out[0][1], 'w')

	print(ascii_boards.render_board(s.board))
	text = "row="+str(out[0][0])+"&col="+str(out[0][1])

	response = app.response_class(
			response=text,
			status=200
			)
	
	print(response.response)
	return response

@app.route("/reset")
def reset():
#print("reset works!")
	s.board.__init__(19)
	ret=open("index.html").read()
	return ret

if __name__ == "__main__":
	app.run(host='0.0.0.0', port='5000', debug=True)




