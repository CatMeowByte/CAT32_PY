# Utilities
# General purpose utilities.
# By CatMeowByte
# SPDX-License-Identifier: WTFPL

# Decorators
def oneshot(func):
 func()
 return None

# Functions
def clamp(value, a, b):
 return max(a, min(value, b))
