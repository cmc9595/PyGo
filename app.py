from flask import Flask, Response, request
import requests
app = Flask(__name__)
from state import State
from net import Net
import torch
import sys
import numpy as np

class PolicyNet(object):
    def __init__(self):
        val = torch.load("Adadelta.pth", map_location=torch.device("cpu"))
        self.model = Net()
        self.model.load_state_dict(val)

    def __call__(self, s):
        b = s.serialize('b')[None] # food for thought
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

#url = 'http://13.125.243.134:5000/white'

@app.route("/")
def hello():
    return open("index.html").read()

@app.route("/move")
def move():

    row = int(request.args["row"])
    col = int(request.args["col"])

    # human
    if not s.play(row, col, 'b'):
        print("Human Can't Play(%d,%d)" % (row, col))
        text = str(s.forhtml())
    else:
        print("Human Move: ", row, col)
        
    
        # computer play 
        out = getRowCol(model(s))
        i = 0
        while 1:
            if s.play(out[i][0], out[i][1], 'w'):
                print("Computer Move: ", out[i][0], out[i][1], out[i][2])
                for j in range(0, 10):
                    print(out[j][0],out[j][1],out[j][2])
                break
            else:
                if i==360:
                    print("All Move illegal")
                    break
                i += 1
        pos = []
        for p in range(10):
            pos.append((out[p][0], out[p][1]))

        text = str(s.forhtml()) + "&"+str(out[i][0])+"&"+str(out[i][1])
        s.printboard_with_pos(pos)

    #text = "row=" + str(out[i][0]) + "&col=" + str(out[i][1])
    response = app.response_class(
            response=text,
            status=200
            )
    
    return response

@app.route("/reset")
def reset():
    #print("reset works!")
    s.board.__init__(19)
    return hello()
    #ret = open("i.html").read()
    #return ret

if __name__ == "__main__":
    app.run(host='0.0.0.0', port='5000', debug=True)




