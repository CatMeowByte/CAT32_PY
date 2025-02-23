# Utilities
# General purpose utilities.
# By CatMeowByte
# SPDX-License-Identifier: WTFPL

import random

# Decorators
def oneshot(func):
 func()
 return None

# Functions
def clamp(value, a, b):
 return max(a, min(value, b))

def remap(value, from_a, from_b, to_a, to_b):
 return to_a + (value - from_a) / (from_b - from_a) * (to_b - to_a)

def rnd(value=1.0):
 return random.random() * value

def link(*parts):
 sep = "/"
 if not parts: return ""

 base, *rest = parts
 path = base.rstrip(sep) if base else ""
 if base and all(ch == sep for ch in base): path = sep

 frags = [p.strip(sep) for p in rest if p]
 if path == sep: return sep + sep.join(frags)
 if not frags: return path
 if path: return sep.join([path] + frags)
 return sep.join(frags)
