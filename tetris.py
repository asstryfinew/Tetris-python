import pygame
import random
import copy
from pygame.locals import *

# This is just a simple tetris game to train myself to real project, the code is not perfect and if you spot issues or things that can be better
# in my code, please let me know ^^

# TODO :
# - Call get_last/first_x/y() functions only once for each rotation (the first or last x will always be the same)
# - Creating a board to manage collisions
# - Implement the score functions and levels
# - Settings menu
# - 

pygame.init()
global clock, settings
clock = pygame.time.Clock()

score_font = pygame.font.SysFont("Hack", 22)

settings = {""}

def get_last_y(representation):
	last_y = 0
	for idxy, y in enumerate(representation):
		for x in y:
			if x==1 and idxy>last_y:
				last_y = idxy
	return last_y
def get_last_x(representation):
	last_x = 0
	for idxy, y in enumerate(representation):
		for idxx, x in enumerate(y):
			if x == 1 and idxx>last_x:
				last_x = idxx
	return last_x
def get_first_x(representation):
	first_x = 999
	for idxy, y in enumerate(representation):
		for idxx, x in enumerate(y):
			if x == 1 and idxx <first_x:
				first_x = idxx
	print(first_x)
	return first_x
def get_first_y(representation):
	first_y = 0
	for idxy, y in enumerate(representation):
		for x in y:
			if x==1:
				first_y = idxy
				return first_y
class Piece:
	def __init__(self, x=5, y=0):
		self.x = x
		self.y = y

		self.color = ()

		self.falling = True
		self.fall_speed = 3
	# drawing the piece
	def draw(self, window):
		for y,line in enumerate(self.representation):
			for x,column in enumerate(line):
				if column == 1:
					pygame.draw.rect(window, self.color, (self.x*25+x*25+50, self.y*25+y*25+50, 25,25))
	# Rotation function (pretty proud of it lol)
	def rotate(self):
		new_repr = [[0 for _ in range(len(self.representation))] for _ in range(len(self.representation[0]))] # grid piece init

		for y, line in enumerate(self.representation):
			for x, column in enumerate(line):
				new_repr[x][y] = self.representation[y][x] # X to Y and Y to X to get the rotation done

		first_x = get_first_x(new_repr)
		if get_first_x(new_repr)+self.x<0: # Check if far-left block is outside the map, if it is, move from 1 block to the right
			self.x+=1
		if not get_last_y(new_repr)+self.y >= 22 and not get_last_x(new_repr)+self.x>=10: # This line check if the new figure will be "out" of the map if it is, do nothing
			self.representation = new_repr
			for x in self.representation:
				x.reverse() # Reverse the grid again to get an asymetric rotation
	def move(self, direction):
		last_x = get_last_x(self.representation)
		first_x = get_first_x(self.representation)
		if direction == "left" and self.x+first_x-1>=0:
			self.x-=1
		if direction == "right" and self.x+last_x+1<10:
			self.x+=1
		


#0000
#0000
#1111
#0000
class I(Piece):
	def __init__(self, x=5,y=0):
		Piece.__init__(self, x,y)
		self.representation = [
		[0,0,0,0],
		[1,1,1,1],
		[0,0,0,0]]
		self.color = (37, 204, 247)
# 0000
# 0110
# 0110
# 0000
class O(Piece):
	def __init__(self, x=5,y=0):
		Piece.__init__(self, x,y)
		self.representation = [[0,0,0,0],
								[0,1,1,0],
								[0,1,1,0],
								[0,0,0,0],
								]
		self.color = (234, 181, 67)
# 000
# 111
# 100
class L(Piece):
	def __init__(self, x=5,y=0):
		Piece.__init__(self, x,y)
		self.representation=[[0,0,0],
							[1,1,1],
							[1,0,0]]
		self.color = (249, 127, 81)
#000
#111
#010
class T(Piece):
	def __init__(self, x=5,y=0):
		Piece.__init__(self, x,y)
		self.representation=[[0,0,0],
							[1,1,1],
							[0,1,0]]
		self.color = (109, 33, 79)
# 111
# 001
class J(Piece):
	def __init__(self, x=5,y=0):
		Piece.__init__(self, x,y)
		self.representation=[[0,0,0],
							[1,1,1],
							[0,0,1]]
		self.color = (59, 59, 152)
# 000
# 110
# 011
class Z(Piece):
	def __init__(self, x=5,y=0):
		Piece.__init__(self, x,y)
		self.representation=[[0,0,0],
							[1,1,0],
							[0,1,1]]
		self.color = (253, 114, 114)
# 000
# 011
# 110
class S(Piece):
	def __init__(self, x=5,y=0):

		Piece.__init__(self, x,y)
		self.representation=[
							[0,0,0],
							[0,1,1],
							[1,1,0]]
		self.color = (189, 197, 129)

# MAIN GAME CLASS
class Game:
	def __init__(self):
		self.settings = {"fall_speed":1}
		self.fps = 15

		self.px_window_width = 350
		self.px_window_height = 650

		self.window = pygame.display.set_mode((self.px_window_width, self.px_window_height))

		self.board = [[None for _ in range(10)] for _ in range(22)]
		self.static_pieces = []
		self.current_piece = I()

		self.score = 0
		self.score_text = score_font.render("Score : {0}".format(self.score), False, (255,255,255))

		self.previous_key = None
		self.action_delay = 0

		self.last_fall = 0

	# Spawn new piece and freeze the previous one
	def spawn_piece(self):
		for idxy, y in enumerate(self.current_piece.representation):
			for idxx, x in enumerate(y):
				if x == 1:	
					self.board[idxy+self.current_piece.y][idxx+self.current_piece.x] = self.current_piece.color
		full_lines = self.full_line()
		for l in full_lines:
			self.score+=100
			self.fall_all(1,0,l)
		self.current_piece = random.choice([I(), O(), L(), T(), J(), Z(), S()])
		self.score+=10
		if self.collide(self.current_piece):
			exit(1)
	# Render the old elements
	def render_board(self):
		pygame.draw.line(self.window, (255,255,255), (50,50), (self.px_window_width-50, 50))
		pygame.draw.line(self.window, (255,255,255), (50,50), (50, self.px_window_height-50))
		pygame.draw.line(self.window, (255,255,255), (50, self.px_window_height-50), (self.px_window_width-50, self.px_window_height-50))
		pygame.draw.line(self.window, (255,255,255), (self.px_window_width-50, 50), (self.px_window_width-50, self.px_window_height-50))
		for idxy, y in enumerate(self.board):
			for idxx, x in enumerate(y):
				if x:
					pygame.draw.rect(self.window, x, (idxx*25+50, idxy*25+50, 25, 25))

	# Check for collision, return True if any collisions detected
	def collide(self, piece):
		# Check the least high block
		last_y = get_last_y(piece.representation)
		if last_y+piece.y+1>=22:
			return True

		for idxy, y in enumerate(piece.representation):
			for idxx, x in enumerate(y):
				if x == 1:
					if self.board[idxy+piece.y+1][idxx+piece.x]:
						return True

	# Fall method to make the current piece... well. fall
	def fall(self, forced=False, hard=False):
		# Timer based falling method (if forced == True then the timer is not used anymore)
		self.last_fall += clock.get_time()
		if self.last_fall > self.current_piece.fall_speed*200 and forced == False:
			self.current_piece.y +=1
			self.last_fall = 0

			if self.collide(self.current_piece):
				self.spawn_piece()
		if forced == True:
			if hard==True:
				while self.collide(self.current_piece) != True:
					self.current_piece.y+=1
			else:
				self.current_piece.y+=1

	# y-=1 for all lines of the game in start_y to end_y
	# Height is the number of time where y-=1 is applied
	def fall_all(self, height, start_y, end_y):
		for _ in range(height):
			for i in reversed(range(start_y, end_y)):
				prev_board = copy.deepcopy(self.board)
				self.board[i+1] = prev_board[i]

	def full_line(self):
		counter = 0
		lines = []
		for idxy, y in enumerate(self.board):
			for x in y:
				if x:
					counter+=1
			if counter == 10:
				lines.append(idxy)
			counter = 0
		return lines


	# Main game events
	def handle_events(self):
		keys = pygame.key.get_pressed()
		for e in pygame.event.get():
			if e.type == pygame.QUIT:
				pygame.quit()
				exit(1)
			if e.type == pygame.KEYDOWN:

				# Move part
				before = copy.deepcopy(self.current_piece)
				if e.key == pygame.K_LEFT:
					self.current_piece.move("left")
				if e.key == pygame.K_RIGHT:
					self.current_piece.move("right")

				self.previous_key = e.key
				if self.collide(self.current_piece): # If it collide, return to the previous position
					self.current_piece = before
				

				# Piece logic (fall, rotation)
				if e.key == pygame.K_LSHIFT:
					self.fall(forced=True, hard=True)
				if e.key == pygame.K_DOWN:
					self.fall(forced=True)
				if e.key == pygame.K_r:
					self.current_piece.rotate()

				if self.collide(self.current_piece):
					self.spawn_piece()
	def run(self):
		while True:
			self.window.fill((0,0,0))
			clock.tick(self.fps)

			self.score_text = score_font.render("Score : {0}".format(self.score), False, (255,255,255))

			# Current piece operation
			self.fall()
			self.handle_events()
			self.current_piece.draw(self.window)
			self.window.blit(self.score_text, (0,0))

			self.render_board()
			pygame.display.flip()
pygame.key.set_repeat(1)
game = Game()
game.run()