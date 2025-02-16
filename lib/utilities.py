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

def rnd(value=1.0):
 return random.random() * value
