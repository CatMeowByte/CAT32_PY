import asyncio
import builtins
import os
import random
import sys
import time

# Libraries
from lib.boxdict import Box
builtins.Box = Box

from lib.utilities import clamp, oneshot
builtins.oneshot = oneshot
builtins.clamp = clamp

# TODO:
# process is a pool
# maximum is 8 process
# use asyncio to run task in parallel
# process 0 is application
# others are service
# 1.menu, 2.input, 3.clock 4.network
# when error it gets removed, not popped << needs to be implemented

# Constants
builtins.TICK = 30
MAX_PROCESSES = 4
BANKS = [
 "_sprite_",
 "_layout_",
 "_tracks_",
]
LAUNCHER = "/app/file_explorer.app"

# Platform specific
builtins.MICROPYTHON = sys.implementation.name == "micropython"
builtins.ROOT = "/" if MICROPYTHON else os.path.dirname(os.path.abspath(__file__))

# HW
# Platform specific imports
@oneshot
def platform_specific_module():
 module_map = {
  "VIDEO": "video",
  "COLOR": "color",
  "FONT": "font",
  "BUTTON": "button",
  "STORAGE": "storage",
 }
 dir_prefix = "console" if MICROPYTHON else "desktop"
 for builtin_name, module_suffix in module_map.items():
  module = __import__(f"hw.{dir_prefix}.{module_suffix}", fromlist=["*"])
  setattr(builtins, builtin_name, module)
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
# COLOR
builtins.mask = COLOR.transparent
# BUTTON
builtins.btn = BUTTON.is_pressed
builtins.btnr = BUTTON.get_repeat
# STORAGE
builtins.link = STORAGE.link
builtins.lsd = STORAGE.lsd

# Internal
def _exception_error(e, pid, at):
 error_type = type(e).__name__
 error_message = str(e)
 tb = e.__traceback__
 while tb.tb_next:
  tb = tb.tb_next
 line_number = tb.tb_lineno

 print(f"{at} ERROR")
 print(processes[pid]._filepath_)
 print(f"{line_number}: {error_type}")
 print(error_message)

# Process
PROCESSES_FIELDS = Box(
 tick=Box(label="UPDATE", interval=1/TICK),
 draw=Box(label="DRAW", interval=1/TICK),
 # Periodic
 period_q=Box(label="PERIOD QUARTER SECOND", interval=1/4),
 period_h=Box(label="PERIOD HALF SECOND", interval=1/2),
 # Generated
 **{
     f"period_{secs}": Box(
         label=f"PERIOD {secs} SECOND",
         interval=secs
     )
     for secs in (1, 2, 4, 8, 16, 32)
 }
)

processes_upref = Box({
 field: [None] * MAX_PROCESSES
 for field in PROCESSES_FIELDS
})

processes = [None] * MAX_PROCESSES

def run(script, pid=0):
 pid = clamp(pid, 0, MAX_PROCESSES - 1)
 kill(pid)
 processes[pid] = type("", (), {})()  # Empty object
 path = link(ROOT, script)

 processes[pid]._filepath_ = path.rsplit("/" if MICROPYTHON else os.path.sep, 1)[-1]
 processes[pid]._pid_ = pid

 lines = None
 with open(path, "r") as f: lines = f.readlines()

 for line in lines:
  for bank in BANKS:
   if line.startswith(bank):
    exec(line, processes[pid].__dict__)

 try:
  exec("".join(lines), processes[pid].__dict__)
 except Exception as e:
  _exception_error(e, pid, "LOAD")
  kill(pid)
  print(f"process {pid} killed.")

 for field in PROCESSES_FIELDS:
  attr = "update" if field == "tick" else field # Exception
  processes_upref[field][pid] = getattr(processes[pid], attr, None)

 # Init
 try:
  processes[pid].init()
 except AttributeError: pass
 except Exception as e:
  _exception_error(e, pid, "INIT")
  kill(pid)
  print(f"process {pid} killed.")

# FIXME: if running is autoupdating the current process and ref, and killing is blanking it, then what is stop?
def stop():
 run(LAUNCHER)

def kill(pid):
 for field in processes_upref:
  processes_upref[field][pid] = None
 processes[pid] = None

# Generic
def timer(duration):
 time.sleep(duration)

def rnd(value=1.0):
 return random.random() * value

# Process
builtins.run = run
builtins.stop = stop
# Generic
builtins.timer = timer
builtins.rnd = rnd

@oneshot
def load_services():
 services = []
 for file in os.listdir(link(ROOT, "svc")):
  if file.endswith(".svc"):
   services.append(file)

 for i, service in enumerate(services):
  if i < MAX_PROCESSES - 1:
   run(link("svc", service), i + 1)

run("/app/file_explorer.app")
# run("/app/planet_name.app")
# run("/app/snake.app")
# run("/test.app")

# Loop
builtins.process = None # Reference of current iterated process
async def asyncio_tick():
 f = PROCESSES_FIELDS.tick
 while True:
  BUTTON._update_state()
  for i, upref in enumerate(processes_upref.tick):
   if not upref: continue
   builtins.process = processes[i]
   try:
    upref()
   except Exception as e:
    _exception_error(e, i, f.label)
    kill(pid)
    print(f"process {pid} killed.")
  await asyncio.sleep(f.interval)

async def asyncio_draw():
 f = PROCESSES_FIELDS.draw
 while True:
  for i, upref in enumerate(processes_upref.draw):
   if not upref: continue
   builtins.process = processes[i]
   mem(0)
   try:
    upref()
   except Exception as e:
    _exception_error(e, i, f.label)
    kill(pid)
    print(f"process {pid} killed.")
  VIDEO.flip()
  await asyncio.sleep(f.interval)

def generate_asyncio_periodic(field):
 f = PROCESSES_FIELDS[field]
 async def periodic_task():
  while True:
   for i, upref in enumerate(processes_upref[field]):
    if not upref: continue
    builtins.process = processes[i]
    try:
     upref()
    except Exception as e:
     _exception_error(e, i, f.label)
     kill(pid)
     print(f"process {pid} killed.")
   await asyncio.sleep(f.interval)
 return periodic_task

async def asyncio_collection():
 await asyncio.gather(
  asyncio_tick(),
  asyncio_draw(),
  *(
   generate_asyncio_periodic(field)()
   for field in PROCESSES_FIELDS
   if field.startswith("period_")
  )
 )

asyncio.run(asyncio_collection())
