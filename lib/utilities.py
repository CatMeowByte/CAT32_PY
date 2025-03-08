# Utilities
# General purpose utilities.
# By CatMeowByte
# SPDX-License-Identifier: WTFPL

import binascii
import random

# Functions
def clamp(value, a, b):
 return max(a, min(value, b))

def remap(value, from_a, from_b, to_a, to_b):
 return to_a + (value - from_a) / (from_b - from_a) * (to_b - to_a)

def rnd(low=0.0, high=1.0):
 return random.uniform(low, high)

def seed(key=None):
 random.seed(binascii.crc32(str(key).encode("utf-8")) if key else None)

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
