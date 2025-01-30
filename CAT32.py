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

# Decorator
def oneshot(func):
 func()
 return None

# Utilities
def run(script):
 global process
 process = type("", (), {})()  # Empty object
 path = link(ROOT, script)

 if PLATFORM.IS_CONSOLE:
  process.__filename__ = path.rsplit("/", 1)[-1]
 else:
  process.__filename__ = os.path.basename(path)

 code = None
 with open(path, "r") as f:
  code = f.read()
 try:
  exec(code, process.__dict__)
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

def link(*i):
 if not i:
  return ""

 if PLATFORM.IS_DESKTOP:
  return os.path.join(*i)

 base = i[0]
 ex = [p.strip("/") for p in i[1:] if p]
 return base.rstrip("/") + "/" + "/".join(ex) if ex else base

# Internal
def _exception_error(e, exec_type, phase):
 error_type = type(e).__name__
 error_message = str(e)
 tb = e.__traceback__
 while tb.tb_next:
  tb = tb.tb_next
 line_number = tb.tb_lineno

 print(exec_type + " " + phase + " ERROR @ " + str(line_number) + ": " + error_type)
 print(error_message)

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
builtins.lsd = STORAGE.lsd
# CAT32
builtins.ROOT = ROOT
builtins.oneshot = oneshot
builtins.run = run
builtins.quit = quit
builtins.timer = timer
builtins.rnd = rnd
builtins.link = link
builtins.o = print # TODO: better debug print


@oneshot
def load_services():
 global services
 for file in os.listdir(link(ROOT, "svc")):
  if not file.endswith(".svc"):
   continue

  service = type("", (), {})()  # Empty object
  service.__filename__ = file
  path = link(ROOT, "svc", file)
  code = None
  with open(path, "r") as f:
   code = f.read()
  try:
   exec(code, service.__dict__)
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
  try:
   process.update()
  except Exception as e:
   _exception_error(e, "PROCESS \"" + process.__filename__ + "\"", "UPDATE")
   process = None

def per_flip_update():
 global process
 if hasattr(process, "draw"):
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
    service.serve()

   i += 1
  except Exception as e:
   _exception_error(e, "SERVICE \"" + process.__filename__ + "\"", "SERVE")
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
  asyncio_service_update()
 )

asyncio.run(asyncio_collection())
