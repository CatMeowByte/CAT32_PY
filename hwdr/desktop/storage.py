import os

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

 return (dirs, files)
