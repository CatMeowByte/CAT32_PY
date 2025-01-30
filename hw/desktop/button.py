import sdl2

CANCEL = 0
ACCEPT = 1
CONTEXT = 2
SYSTEM = 3
UP = 4
DOWN = 5
LEFT = 6
RIGHT = 7

keybind = {
 CANCEL: [sdl2.SDL_SCANCODE_RSHIFT, sdl2.SDL_SCANCODE_BACKSPACE],
 ACCEPT: [sdl2.SDL_SCANCODE_RETURN, sdl2.SDL_SCANCODE_SPACE],
 CONTEXT: [sdl2.SDL_SCANCODE_E, sdl2.SDL_SCANCODE_GRAVE],
 SYSTEM: [sdl2.SDL_SCANCODE_Q, sdl2.SDL_SCANCODE_ESCAPE],
 UP: [sdl2.SDL_SCANCODE_W, sdl2.SDL_SCANCODE_UP],
 DOWN: [sdl2.SDL_SCANCODE_S, sdl2.SDL_SCANCODE_DOWN],
 LEFT: [sdl2.SDL_SCANCODE_A, sdl2.SDL_SCANCODE_LEFT],
 RIGHT: [sdl2.SDL_SCANCODE_D, sdl2.SDL_SCANCODE_RIGHT],
}

state = [0, 0, 0, 0, 0, 0, 0, 0]

events = sdl2.SDL_Event()

def _update_state():
 global state
 while sdl2.SDL_PollEvent(events):
  pass
 keystate = sdl2.SDL_GetKeyboardState(None)
 for i in range(8):
  if keystate[keybind[i][0]] or keystate[(keybind[i][1])]:
   state[i] += 1
  else:
   state[i] = 0

def is_pressed(button):
 return state[button] > 0

def get_repeat(button, delay=15, interval=5):
 duration = state[button]

 if duration == 1:
  return True
 if duration == delay:
  return True
 if duration > delay and (duration - delay) % interval == 0:
  return True

 return False
