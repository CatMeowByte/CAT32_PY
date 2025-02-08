import os

def link(*point):
 if not point:
  return ""

 base, *ex = point
 path = base if base == "/" else base.rstrip("/")

 for p in ex:
  if p:
   path = os.path.join(path, p.strip(os.sep))

 return path

def lsd(path):
 dirs = []
 files = []

 try:
  for entry in os.listdir(path):
   try:
    os.chdir(path.rstrip("/") + "/" + entry)
    dirs.append(entry)
    os.chdir(path)
   except OSError:
    files.append(entry)
 except OSError:
  pass

 return [dirs, files]
