import os
import sys

# TODO: overwrite all __dict__ usage since it might not work

from lib.boxdict import Box
from lib.utilities import oneshot, clamp, remap, rnd, link

GLOBAL = Box() # Packed variables
STATIC = Box() # Unpacked functions and classes

# Global
GLOBAL.MICROPYTHON = sys.implementation.name == "micropython"
GLOBAL.ROOT = "/" if GLOBAL.MICROPYTHON else os.path.dirname(os.path.abspath(__file__))
GLOBAL.TICK = 30

def make_static(**kwargs): STATIC.update(kwargs)

o = print

make_static(
 STATIC = STATIC, # Reference
 make_static = make_static,
 Box = Box,
 oneshot = oneshot, clamp = clamp, remap = remap, rnd = rnd, link = link,
 o = o,
)

# Header
o("CAT-32")
o("0.0.0-dev")
o("in Console" if GLOBAL.MICROPYTHON else "Desktop Emu.")
o("───────────────")

# Hardware drivers
@oneshot
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
  obj, obj_space = type("", (), {})(), Box()
  with open(path, "r") as f: code = f.read()
  exec(code, obj_space)
  for k, v in obj_space.items(): setattr(obj, k, v)
  setattr(STATIC, obj_name, obj)

# Dependencies
@oneshot
def link_dependencies():
 STATIC.VIDEO.COLOR = STATIC.COLOR
 STATIC.VIDEO.FONT = STATIC.FONT

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

STATIC.VIDEO.init() # Later

TASK_MANAGER = "/core/taskmgr.py"

@oneshot
def start_task_manager():
 obj, obj_space = type("", (), {})(), Box()
 obj_space.GLOBAL = GLOBAL
 obj_space.update(STATIC)
 with open(link(GLOBAL.ROOT, TASK_MANAGER), "r") as f: code = f.read()
 exec(code, obj_space)
 for k, v in obj_space.items(): setattr(obj, k, v)

# TODO: Shutdown sequence