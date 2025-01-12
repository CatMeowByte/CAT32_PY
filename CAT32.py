import asyncio
import builtins
import os
import random
import sys
import time

import hw.button
import hw.color
import hw.font
import hw.storage
import hw.video


ROOT = os.path.dirname(os.path.abspath(__file__))
TICK = 30
DEFAULT_MENU = "/app/file_explorer.app"

process = None
service = None
services = [f for f in os.listdir(ROOT + "/svc") if f.endswith(".svc")]

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
 path = ROOT + "/" + script.lstrip("/")
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

def per_service_update():
 global service, services
 service = type("", (), {})()  # Empty object
 i = 0
 while i < len(services):
  file = services[i]
  try:
   path = ROOT + "/svc/" + file
   code = None
   with open(path, "r") as f:
    code = f.read()
   exec(code, service.__dict__)
   
   if hasattr(service, "serve"):
    service.serve()
   
   i += 1
  except Exception as e:
   error_type = type(e).__name__
   error_message = str(e)
   tb = e.__traceback__
   while tb and tb.tb_next:
    tb = tb.tb_next
   line_number = tb.tb_lineno
   
   print("SERVICE ERROR @ " + str(line_number) + ": " + error_type)
   print(error_message)
   print("service \"" + file + "\" disabled")
   
   services.pop(i)
   # Do not increment `i` because the list has shifted

async def asyncio_tick_update():
 while True:
  per_tick_update()
  await asyncio.sleep(1 / TICK)

async def asyncio_flip_update():
 while True:
  per_flip_update()
  await asyncio.sleep(0)

async def asyncio_service_update():
 while services:
  per_service_update()
  await asyncio.sleep(0)

async def asyncio_collection():
 await asyncio.gather(
  asyncio_tick_update(),
  asyncio_flip_update(),
  asyncio_service_update()
 )

asyncio.run(asyncio_collection())
