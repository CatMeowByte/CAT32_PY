# Box
# Dictionary with dot notation.
# By CatMeowByte
# SPDX-License-Identifier: WTFPL

# Reserved name:
# clear, copy, fromkeys, get, items, keys, pop, popitem, setdefault, update, values

class Box(dict):
 def __getattr__(self, key):
  try:
   return self[key]
  except KeyError:
   raise AttributeError(f"'{key}' not in '{type(self).__name__}'")

 def __setattr__(self, key, value):
  self[key] = value

 def __delattr__(self, key):
  try:
   del self[key]
  except KeyError:
   raise AttributeError(f"'{key}' not in '{type(self).__name__}'")

 def __str__(self):
  items = (f"{k} = {v!r}" for k, v in self.items())
  return type(self).__name__ + "(\n " + ',\n '.join(items) + ",\n)"

 def __repr__(self):
  items = (f"{k}={v!r}" for k, v in self.items())
  return type(self).__name__ + "(" + ', '.join(items) + ")"