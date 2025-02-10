BODY_COUNT = 16
FOOD_COUNT = 32
MAP_SIZE = 30  # Size of the game map

snake = []
dir = [1 , 0]
food = []
f = 0
boost = 1
state = "menu"
menu_sel = 0
menu_items = ["Play", "Options", "Exit"]
options_sel = 0
options_items = ["Sound", "Food Glow"]
sound_enabled = True
highlight_food = True

def init():
 restart()

def update():
 global f, boost
 if state == "menu" or state == "options":
  menu_input()
 else:
  if f % (2 - boost) == 0:
   tick()
  f = (f + 1) % (2 - boost)

def menu_input():
 global state, menu_sel, options_sel
 sel = menu_sel if state == "menu" else options_sel
 items_size = len(menu_items) if state == "menu" else len(options_items)

 if btnr(BUTTON.UP):
  sel = max(sel - 1, 0)
#   play_sound(SND.get_freq("A", 4), 1.0 / 20.0)
 elif btnr(BUTTON.DOWN):
  sel = min(sel + 1, items_size - 1)
#   play_sound(SND.get_freq("A", 4), 1.0 / 20.0)
 elif btnr(BUTTON.ACCEPT):
  if state == "menu":
#    play_sound(SND.get_freq("G", 5), 1.0 / 20.0)
#    play_sound(SND.get_freq("A", 6), 1.0 / 20.0)
   if sel == 0:
    state = "play"
   elif sel == 1:
    state = "options"
   elif sel == 2:
    exit_to_menu()
  elif state == "options":
   if sel == 0:
    sound_enabled = not sound_enabled
   elif sel == 1:
    highlight_food = not highlight_food
#    play_sound(SND.get_freq("G", 5), 1.0 / 20.0)
#    play_sound(SND.get_freq("A", 6), 1.0 / 20.0)
 elif BUTTON.get_repeat(BUTTON.CANCEL):
  if state == "options":
   state = "menu"
  elif state == "play":
   state = "menu"

 if state == "menu":
  menu_sel = sel
 elif state == "options":
  options_sel = sel

# def play_sound(freq, duration):
#  if sound_enabled:
#   SND.play_tone(freq, duration)

def tick():
 global snake, food
 head = [snake[0][0] + dir[0], snake[0][1] + dir[1]]
 snake.insert(0, head)
 if head in food:
  food.remove(head)
#   play_sound(SND.get_freq("C", 7), 1.0 / 30.0)
  spawn_food()
 else:
  snake.pop()

 # Collision with map boundaries
 if head[0] < 0 or head[1] < 0 or head[0] >= MAP_SIZE or head[1] >= MAP_SIZE:
  restart(1)

 for i in range(1, len(snake)):
  if head == snake[i]:
   restart(1)
   break

def input():
 global dir, state, boost
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
 elif btn(BUTTON.CANCEL):
  state = "menu"

def draw():
 if state == "menu" or state == "options":
  draw_menu()
 else:
  input()
  draw_game()

def draw_menu():
 global state
 cam()
 cls(COLOR.DARK_PURPLE)
 title = "SNAKE" if state == "menu" else "OPTIONS"
 text(8, 8, title, COLOR.WHITE)
 mask(COLOR.BLACK, 0)
 mask(COLOR.PINK, 1)
 items = menu_items if state == "menu" else options_items
 sel = menu_sel if state == "menu" else options_sel

 for i in range(len(items)):
  fg = COLOR.WHITE if i == sel else COLOR.GRAY
  bg = COLOR.BLACK if i == sel else COLOR.PINK
  t = items[i]
  if state == "options":
   value = "ON" if (i == 0 and sound_enabled) or (i == 1 and highlight_food) else "OFF"
   t += ": " + value
  text(8, 16 + (i * 8), t, fg, bg)
 mask()

def draw_game():
 global food
 cam((-VIDEO.W + MAP_SIZE) / 2, (-VIDEO.H+ + MAP_SIZE) / 2)
 cls(COLOR.DARK_BLUE)
 rect(-1, -1, MAP_SIZE + 2, MAP_SIZE + 2, COLOR.DARK_GRAY)

 score = str(len(snake) - BODY_COUNT)
 text((MAP_SIZE / 2 - 2 * len(score)), -8, score, COLOR.WHITE)
 for d in food:
  if highlight_food and is_food_in_snake_path(d):
   rect(d[0] - 1, d[1] - 1, 3, 3, COLOR.DARK_GREEN)
   pix(d[0], d[1], COLOR.GREEN)
  else:
   pix(d[0], d[1], COLOR.DARK_GREEN)
 for s in snake:
  pix(s[0], s[1], COLOR.WHITE)

def is_food_in_snake_path(food_pos):
 global snake, dir
 # Check if the food is in the direct path of the snake head
 head = snake[0]
 if dir == [1, 0] and food_pos[1] == head[1] and food_pos[0] > head[0]:
  return True
 elif dir == [-1, 0] and food_pos[1] == head[1] and food_pos[0] < head[0]:
  return True
 elif dir == [0, 1] and food_pos[0] == head[0] and food_pos[1] > head[1]:
  return True
 elif dir == [0, -1] and food_pos[0] == head[0] and food_pos[1] < head[1]:
  return True
 return False

def spawn_food():
 while len(food) < FOOD_COUNT:
  new_food = [int(rnd(MAP_SIZE)), int(rnd(MAP_SIZE))]
  if new_food not in snake and new_food not in food:
   food.append(new_food)

def restart(sound = 0):
 global snake, dir, state
 snake = []
 for s in range(BODY_COUNT):
  snake.append([MAP_SIZE / 2 - s, MAP_SIZE / 2])
 dir = [1, 0]
 spawn_food()
 state = "menu"
#  if sound:
#   play_sound(SND.get_freq("C", 5), 1.0 / 30.0)
#   play_sound(SND.get_freq("B", 4), 1.0 / 30.0)
#   play_sound(SND.get_freq("A", 4), 1.0 / 30.0)
#   play_sound(SND.get_freq("G", 4), 1.0 / 30.0)
