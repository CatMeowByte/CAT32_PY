import builtins
import os
import random
import sys
import threading
# import asyncio
import time

import hw.video
import hw.color
import hw.font
import hw.button

RUNMODE = 0
ROOT = os.path.dirname(os.path.abspath(__file__))
FPS = 30

process = type('', (), {})() # Empty object

def run(script):
 global process
 if RUNMODE:
  directory, file = os.path.split(script)
  module = os.path.splitext(file)[0]
  
  # Temporarily modify sys.path
  original_sys_path = sys.path
  sys.path = original_sys_path + [ROOT + directory]  # Append the directory
  
  process = __import__(module)
  
  # Restore the original sys.path
  sys.path = original_sys_path
 else:
  with open(ROOT + script, "r") as f: # Why os.path.join doesnt work?
   code = f.read()
  exec(code, process.__dict__)

def timer(duration):
 time.sleep(duration)

def rnd(value=1.0):
 return random.random() * value

# Illegal programming technique : builtins injection
builtins.VIDEO = hw.video
builtins.COLOR = hw.color
builtins.FONT = hw.font
builtins.BUTTON = hw.button

VIDEO.COLOR = COLOR
VIDEO.FONT = FONT
VIDEO.init()

builtins.cam = VIDEO.camera
builtins.mem = VIDEO.memsel
builtins.pix = VIDEO.pixel
builtins.line = VIDEO.line
builtins.rect = VIDEO.rect
builtins.text = VIDEO.text
builtins.blit = VIDEO.blit
builtins.cls = VIDEO.clear
builtins.flip = VIDEO.flip

builtins.mask = COLOR.transparent

builtins.btn = BUTTON.is_pressed
builtins.btnr = BUTTON.get_repeat

builtins.run = run
builtins.timer = timer
builtins.rnd = rnd

builtins.o = print

# run("/app/planet_name.cat.py")
run("/app/snake.cat.py")
# run("/test.cat.py")

# Loop
if hasattr(process, "init"):
 process.init()

def per_fps_update():
 BUTTON._update_state()

 if hasattr(process, "update"):
  process.update()

def process_update():
 if hasattr(process, "draw"):
  process.draw()
  flip()

def main():
 time_last_fps  = time.time()
 time_last_flip = time.time()
 while True:
  time_now = time.time()
  # variable fps refresh
  if time_now - time_last_fps  >= 1/FPS:
   time_last_fps += 1/FPS
   per_fps_update()
  # default 60hz refresh
  if time_now - time_last_flip >= 1/60:
   time_last_flip += 1/60
   process_update()
  # dont clog cpu resources
  time.sleep(1/1000)
 return 0
 
if __name__ == "__main__":
 sys.exit(main())

# async def asyncio_process_update():
#  while True:
#   process_update()
#   await asyncio.sleep(0)  # Yield
# 
# async def asyncio_fps_update():
#  while True:
#   per_fps_update()
#   await asyncio.sleep(1 / FPS)  # Yield
# 
# async def asyncio_collection():
#  await asyncio.gather(asyncio_process_update(), asyncio_fps_update())
# 
# asyncio.run(asyncio_collection())