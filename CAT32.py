import builtins
import os
import random
import sys
import asyncio
import time

import hw.video
import hw.color
import hw.font
import hw.button
import hw.storage


ROOT = os.path.dirname(os.path.abspath(__file__))
TICK = 30
DEFAULT_MENU = "/app/file_explorer.app"

process = None
service = None

def process_error(e, phase):
 global process
 error_type = type(e).__name__
 error_message = str(e)
 tb = e.__traceback__
 while tb.tb_next:
  tb = tb.tb_next
 line_number = tb.tb_lineno
 
 print(phase + " ERROR @ " + str(line_number) + ": " + error_type)
 print(error_message)
 process = None

def run(script):
 global process
 process = type("", (), {})()  # Empty object
 path = ROOT.rstrip('/') + '/' + script.lstrip('/')
 code = None
 with open(path, "r") as f:
  code = f.read()
 try:
  exec(code, process.__dict__)
 except Exception as e:
  process_error(e, "LOAD")

 if hasattr(process, "init"):
  try:
   process.init()
  except Exception as e:
   process_error(e, "INIT")

def timer(duration):
 time.sleep(duration)

def rnd(value=1.0):
 return random.random() * value

# Illegal programming technique: builtins injection
# HW
builtins.VIDEO = hw.video
builtins.COLOR = hw.color
builtins.FONT = hw.font
builtins.BUTTON = hw.button
builtins.STORAGE = hw.storage
# VIDEO
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
# COLOR
builtins.mask = COLOR.transparent
# BUTTON
builtins.btn = BUTTON.is_pressed
builtins.btnr = BUTTON.get_repeat
# STORAGE
builtins.lsd = STORAGE.lsd
# CAT32
builtins.ROOT = ROOT
builtins.run = run
builtins.timer = timer
builtins.rnd = rnd
builtins.o = print

run("/app/file_explorer.app")
# run("/app/planet_name.app")
# run("/app/snake.app")
# run("/test.app")

# Loop
def per_tick_update():
 BUTTON._update_state()

 if hasattr(process, "update"):
  try:
   process.update()
  except Exception as e:
   process_error(e, "UPDATE")

def per_flip_update():
 if hasattr(process, "draw"):
  try:
   process.draw()
  except Exception as e:
   process_error(e, "DRAW")
  flip()

async def asyncio_tick_update():
 while True:
  per_tick_update()
  await asyncio.sleep(1 / TICK)

async def asyncio_flip_update():
 while True:
  per_flip_update()
  await asyncio.sleep(0)

async def asyncio_collection():
 await asyncio.gather(asyncio_tick_update(), asyncio_flip_update())

asyncio.run(asyncio_collection())
