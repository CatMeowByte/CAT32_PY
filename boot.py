import os
import sys

from lib.boxdict import Box
from lib.utilities import oneshot, clamp, remap, rnd, link

STATIC = Box() # Unpacked functions and classes
GLOBAL = Box() # Packed variables

def make_static(*args): STATIC.update({arg.__name__ : arg for arg in args})

make_static(
 Box,
 oneshot, clamp, remap, rnd, link,
)

# Global
GLOBAL.MICROPYTHON = sys.implementation.name == "micropython"
GLOBAL.ROOT = "/" if GLOBAL.MICROPYTHON else os.path.dirname(os.path.abspath(__file__))
GLOBAL.TICK = 30

# Header
print("CAT-32")
print("0.0.0-dev")
print("in Console" if GLOBAL.MICROPYTHON else "Desktop Emu.")
print("───────────────")

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
  with open(path) as f:
   code = f.read()
  container = type(obj_name, (), {})()  # Empty object
  exec(code, container.__dict__)
  setattr(STATIC, obj_name, container)

print(STATIC)
print(GLOBAL)