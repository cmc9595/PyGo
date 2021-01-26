import sys
sys.setrecursionlimit(5000)

arr = [["." for _ in range(19)]for _ in range(19)]
side = {"w":"o", "b":"#"}

class Cluster(object):
	def __init__(self, row, col, color):

		self.visited = [[0 for _ in range(19)]for _ in range(19)]
		self.cluster = []
		self.border = []
		self.point = [row, col, color]

		if arr[row][col] != side[color]:
			#print("For (%d, %d), cluster init fail: wrong color" % (row, col))
			return
		self.dfs(row, col, color) #make Visited map
		self.get_cluster()
		self.get_cluster_border()

	def dfs(self, row, col, color):
		if arr[row][col] != side[color]:
			print("dfs: wrong color or empty space")
			return False
		self.visited[row][col] = 1
		for i in [[row+1, col], [row-1, col], [row, col+1], [row, col-1]]:
			if arr[i[0]][i[1]]==side[color] and 0<=i[0]<=18 and 0<=i[1]<=18 and self.visited[i[0]][i[1]]==0: # visit이 있어야 종료조건.
				self.dfs(i[0], i[1], color)

	def get_cluster(self):
		for idx, i in enumerate(self.visited):
			for jdx, j in enumerate(i):
				if j==1:
					self.cluster.append((idx, jdx))

	def get_cluster_border(self):
		if len(self.cluster)==0:
			print("get cluster border error:cluster len=0")
			return
		for i in range(19):
			for j in range(19):
				if (i, j) not in self.cluster:
					if (i+1, j) in self.cluster and i+1<=18:
						self.border.append((i, j))
					if (i-1, j) in self.cluster and 0<=i-1:
						self.border.append((i, j))
					if (i, j+1) in self.cluster and j+1<=18:
						self.border.append((i, j))
					if (i, j-1) in self.cluster and 0<=j-1:
						self.border.append((i, j))
		self.border = list(set(self.border))

	def print_cluster(self):
		print("point : ", self.point[0], self.point[1], self.point[2])
		print("cluster : ", self.cluster)
		print("border : ", self.border)
		print()
			

def is_capturing_move(row, col, color): #returns captured clusters in LIST
	#check emptiness										 
	if arr[row][col]!=".":
		return False

	l = []
	for i in [[row+1, col], [row-1, col], [row, col+1], [row, col-1]]:
		if 0<=i[0]<=18 and 0<=i[1]<=18:
			new_cluster = Cluster(i[0], i[1], 'b' if color=='w' else 'w') #opposite color
			if len(new_cluster.cluster)==0:
				continue

			f = True
			for j in set(new_cluster.border)-set([(row,col)]):
				#print(set(new_cluster.border)-set([(row,col)]))
				#print(j)
				if arr[j[0]][j[1]] != side[color]:
					f = False
					break
			if f==True:
				l.append(new_cluster.cluster)

	if l is None:
		return False
	else:
		return l

def is_suicide_move(row, col, color):
	if arr[row][col]!=".":
		return False
	#(row, col) 포함한 cluster(only 1 exists)가 둘러쌓여있는지만 찾으면 끝!
	arr[row][col] = side[color] ##임시로 채운다.
	new_cluster = Cluster(row, col, color)
	arr[row][col] = "."  #다시 꺼낸다.
	#print(new_cluster.cluster)
	#print(new_cluster.border)
	
	for i in new_cluster.border:
		if arr[i[0]][i[1]] != ('#' if color=='w' else 'o'):
			return False #둘러쌓이지 않다면 false
	
	return True
			

	
def play(row, col, color):
	if arr[row][col]!=".":
		return False

	arr[row][col] = side[color]

	'''
	if is_suicide_move()  and is_capturing_move():
		if 이전 내 수:
			#no play
		else:
			#play
	elif not suicide and capturing:
		#play
	elif suicide and not capture:
		#no play
	else not suicide and not capture:
		#play
	'''

def printboard():
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
play(3, 3, 'w')
play(3, 4, 'b')
play(3, 2, 'b')
play(15, 3, 'b')
play(3, 15, 'w')
play(3, 17, 'w')
play(2, 16, 'w')
play(4, 16, 'w')
play(10, 10, 'w')
play(10, 11, 'w')
play(10, 12, 'w')
play(10, 13, 'w')
play(9, 10, 'w')
play(9, 9, 'w')
play(9, 9, 'w')
play(9, 9, 'w')
play(6, 2, 'b')
play(7, 2, 'b')
play(0, 0, 'w')
play(0, 1, 'w')
play(0, 2, 'b')
play(4, 1, 'b')
play(4, 2, 'w')
play(4, 4, 'w')
play(4, 5, 'b')
play(5, 2, 'b')
play(6, 3, 'b')
play(5, 4, 'b')
play(4, 5, 'b')
play(5, 3, 'w')
play(0, 3, 'w')
play(1, 3, 'w')
play(2, 3, 'w')
play(0, 2, 'b')
play(1, 2, 'b')
play(2, 2, 'b')
play(0, 4, 'b')
play(1, 4, 'b')
play(2, 4, 'b')
play(1, 0, 'b')
play(1, 1, 'w')


#c1 = Cluster(3, 3, 'w').print_cluster()
printboard()

print(is_capturing_move(0, 0, 'b'))

for i in range(19):
	for j in range(19):
		if is_capturing_move(i, j, 'w'):
			print(i, j, 'w', is_capturing_move(i, j, 'w'))
		if is_capturing_move(i, j, 'b'):
			print(i, j, 'b', is_capturing_move(i, j, 'b'))

