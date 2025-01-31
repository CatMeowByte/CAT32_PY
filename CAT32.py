import asyncio
import builtins
import os
import random
import sys
import time

# Device specific implementation
builtins.PLATFORM = type("", (), {})()
PLATFORM.IS_CONSOLE = sys.implementation.name == "micropython"
PLATFORM.IS_DESKTOP = sys.implementation.name == "cpython"

ROOT = "/" if PLATFORM.IS_CONSOLE else os.path.dirname(os.path.abspath(__file__))
TICK = 30
LAUNCHER = "/app/file_explorer.app"

process = None
services = []

# Injected into builtins
banks = [
 "__sprite__",
]

# Decorator
def oneshot(func):
 func()
 return None

# Builtins injection
# HW
# Platform specific imports
@oneshot
def platform_specific_module():
 hw_prefix = "hw.console." if PLATFORM.IS_CONSOLE else "hw.desktop."
 builtins.VIDEO = __import__(hw_prefix + "video", fromlist=["*"])
 builtins.COLOR = __import__(hw_prefix + "color", fromlist=["*"])
 builtins.FONT = __import__(hw_prefix + "font", fromlist=["*"])
 builtins.BUTTON = __import__(hw_prefix + "button", fromlist=["*"])
 builtins.STORAGE = __import__(hw_prefix + "storage", fromlist=["*"])
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
builtins.link = STORAGE.link
builtins.lsd = STORAGE.lsd

# Utilities
def run(script):
 global process
 process = type("", (), {})()  # Empty object
 path = link(ROOT, script)

 process.__filename__ = path.rsplit("/" if PLATFORM.IS_CONSOLE else os.path.sep, 1)[-1]

 def __point_self__():
  return process.__dict__
 process.__point_self__ = __point_self__

 lines = None
 with open(path, "r") as f: lines = f.readlines()

 for line in lines:
  for bank in banks:
   if line.startswith(bank):
    exec(line, builtins.__dict__)

 try:
  exec("".join(lines), process.__dict__)
 except Exception as e:
  _exception_error(e, "PROCESS \"" + process.__filename__ + "\"", "LOAD")
  process = None

 if hasattr(process, "init"):
  try:
   process.init()
  except Exception as e:
   _exception_error(e, "PROCESS \"" + process.__filename__ + "\"", "INIT")
   process = None

def quit():
 run(LAUNCHER)

def timer(duration):
 time.sleep(duration)

def rnd(value=1.0):
 return random.random() * value

# CAT32
builtins.ROOT = ROOT
builtins.oneshot = oneshot
builtins.run = run
builtins.quit = quit
builtins.timer = timer
builtins.rnd = rnd
builtins.o = print # TODO: better debug print

# Internal
def _exception_error(e, exec_type, phase):
 error_type = type(e).__name__
 error_message = str(e)
 tb = e.__traceback__
 while tb.tb_next:
  tb = tb.tb_next
 line_number = tb.tb_lineno

 print(exec_type + " " + phase + " ERROR")
 print(str(line_number) + ": " + error_type)
 print(error_message)

@oneshot
def load_services():
 global services
 for file in os.listdir(link(ROOT, "svc")):
  if not file.endswith(".svc"):
   continue

  service = type("", (), {})()  # Empty object
  path = link(ROOT, "svc", file)

  service.__filename__ = file

  lines = None
  with open(path, "r") as f: lines = f.readlines()

  for line in lines:
   for bank in banks:
    if line.startswith(bank):
     exec(line, builtins.__dict__)

  try:
   exec("".join(lines), service.__dict__)
  except Exception as e:
   _exception_error(e, "SERVICE \"" + service.__filename__ + "\"", "LOAD")
   print("service \"" + service.__filename__ + "\" skipped")
   continue

  services.append(service)

run("/app/file_explorer.app")
# run("/app/planet_name.app")
# run("/app/snake.app")
# run("/test.app")

# Loop
def per_tick_update():
 global process
 BUTTON._update_state()

 if hasattr(process, "update"):
  for bank in banks:
   if hasattr(process, bank):
    builtins.__dict__[bank] = process.__dict__[bank]
  try:
   process.update()
  except Exception as e:
   _exception_error(e, "PROCESS \"" + process.__filename__ + "\"", "UPDATE")
   process = None

def per_flip_update():
 global process
 if hasattr(process, "draw"):
  for bank in banks:
   if hasattr(process, bank):
    builtins.__dict__[bank] = process.__dict__[bank]
  try:
   process.draw()
  except Exception as e:
   _exception_error(e, "PROCESS \"" + process.__filename__ + "\"", "DRAW")
   process = None
  flip()

def per_service_update():
 global services
 i = 0
 while i < len(services):
  service = services[i]
  try:
   if hasattr(service, "serve"):
    for bank in banks:
     if hasattr(service, bank):
      builtins.__dict__[bank] = service.__dict__[bank]
    service.serve()

   i += 1
  except Exception as e:
   _exception_error(e, "SERVICE \"" + service.__filename__ + "\"", "SERVE")
   print("service \"" + service.__filename__ + "\" disabled")

   services.pop(i)
   # Do not increment `i` because the list has shifted

async def asyncio_tick_update():
 while True:
  per_tick_update()
  await asyncio.sleep(1 / TICK)

async def asyncio_flip_update():
 while True:
  per_flip_update()
  await asyncio.sleep(1 / TICK)

async def asyncio_service_update():
 while services:
  per_service_update()
  await asyncio.sleep(1 / TICK)

async def asyncio_collection():
 await asyncio.gather(
  asyncio_tick_update(),
  asyncio_flip_update(),
  asyncio_service_update(),
 )

asyncio.run(asyncio_collection())
