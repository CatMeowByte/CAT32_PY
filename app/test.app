# CAT32

pos = [0, 0]
dir = [1 , 0]

def init():
 print("INIT!!")

def update():
 global pos
 input()
 pos[0] = (pos[0] + dir[0]) % VIDEO.W
 pos[1] = (pos[1] + dir[1]) % VIDEO.H

def draw():
 cls(COLOR.DARK_BLUE)
 line(0, 0, 120, 120, COLOR.WHITE)
 text(8, 16, "Hi, all!", COLOR.YELLOW)
 text(0, VIDEO.H - 8, str(BUTTON.state), COLOR.GRAY)
 pix(pos[0], pos[1], COLOR.PINK)

def input():
 global dir
 boost = 0
 if btn(BUTTON.UP) and dir != [0, 1]:
  if dir == [0, -1]:
   boost = 1
  dir = [0, -1]
 elif btn(BUTTON.DOWN) and dir != [0, -1]:
  if dir == [0, 1]:
   boost = 1
  dir = [0, 1]
 elif btn(BUTTON.LEFT) and dir != [1, 0]:
  if dir == [-1, 0]:
   boost = 1
  dir = [-1, 0]
 elif btn(BUTTON.RIGHT) and dir != [-1, 0]:
  if dir == [1, 0]:
   boost = 1
  dir = [1, 0]