import os
import sys

# TODO: overwrite all __dict__ usage since it might not work

from lib.boxdict import Box
from lib.utilities import clamp, remap, rnd, link

GLOBAL = Box() # Packed variables
STATIC = Box() # Unpacked functions and classes

# Global
GLOBAL.MICROPYTHON = sys.implementation.name == "micropython"
GLOBAL.ROOT = "/" if GLOBAL.MICROPYTHON else os.path.dirname(os.path.abspath(__file__))
GLOBAL.TICK = 30
GLOBAL.STATIC = STATIC # Reference

o = print

def make_static(**kwargs): STATIC.update(kwargs)

def bind(path):
 path_key = f"bind:{path}"

 if path_key not in sys.modules:
  obj, obj_space = type(path_key, (), {})(), Box()
  obj_space.GLOBAL = GLOBAL
  obj_space.update(STATIC)
  with open(link(GLOBAL.ROOT, path)) as f: code = f.read()
  exec(code, obj_space)
  for k, v in obj_space.items(): setattr(obj, k, v)
  sys.modules[path_key] = obj

 return sys.modules[path_key]

make_static(
 Box = Box,
 clamp = clamp, remap = remap, rnd = rnd, link = link,
 o = o,
 make_static = make_static,
 bind = bind,
)

# Header
o("CAT-32")
o("0.0.0-dev")
o("in Console" if GLOBAL.MICROPYTHON else "Desktop Emu.")
o("───────────────")

# Hardware drivers
def add_hardware_drivers():
 hwdr_map = {
  "VIDEO": "video",
  "COLOR": "color",
  "FONT": "font",
  "BUTTON": "button",
  "STORAGE": "storage",
 }
 hwdr_dev = "console" if GLOBAL.MICROPYTHON else "desktop"
 for obj_name, hwdr_file in hwdr_map.items():
  path = link("hwdr", hwdr_dev, hwdr_file + ".py")
  obj, obj_space = type(f"hwdr:{path}", (), {})(), Box()
  obj_space.GLOBAL = GLOBAL
  obj_space.update(STATIC)
  with open(link(GLOBAL.ROOT, path), "r") as f: code = f.read()
  exec(code, obj_space)
  for k, v in obj_space.items(): setattr(obj, k, v)
  setattr(STATIC, obj_name, obj)
add_hardware_drivers()

# Dependencies
STATIC.VIDEO.depends(
 COLOR = STATIC.COLOR,
 FONT = STATIC.FONT,
)

make_static(
 # VIDEO
 cam = STATIC.VIDEO.camera,
 mem = STATIC.VIDEO.memsel,
 pix = STATIC.VIDEO.pixel,
 line = STATIC.VIDEO.line,
 rect = STATIC.VIDEO.rect,
 text = STATIC.VIDEO.text,
 blit = STATIC.VIDEO.blit,
 cls = STATIC.VIDEO.clear,

 # COLOR
 mask = STATIC.COLOR.transparent,

 # BUTTON
 btn = STATIC.BUTTON.is_pressed,
 btnr = STATIC.BUTTON.get_repeat,

 # STORAGE
 lsd = STATIC.STORAGE.lsd,
)

# Initialize
STATIC.VIDEO.init()

# Process Manager
PROCESS_MANAGER = "/core/procmgr.py"

def start_process_manager():
 obj, obj_space = type(f"procmgr:{PROCESS_MANAGER}", (), {})(), Box()
 obj_space.GLOBAL = GLOBAL
 obj_space.update(STATIC)
 with open(link(GLOBAL.ROOT, PROCESS_MANAGER), "r") as f: code = f.read()
 exec(code, obj_space)
 for k, v in obj_space.items(): setattr(obj, k, v)
start_process_manager()

# Shutdown
o("───────────────")
o("Shutdown")