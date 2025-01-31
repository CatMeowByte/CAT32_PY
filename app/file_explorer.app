path = "/"
ls_dir = []
ls_file = []
entries = []
select = 0

def init():
 load_directory()

def load_directory():
 global ls_dir, ls_file, entries, select
 ls = lsd(link(ROOT, path))
 ls_dir = ls[0]
 ls_file = ls[1]
 ls_dir.sort()
 ls_file.sort()
 entries = ls_dir + ls_file
 select = 0

def path_back(path):
 path = path.rstrip("/")
 last_slash = path.rfind("/")
 return path[:last_slash] if last_slash > 0 else "/"

def update():
 global select, path
 sp = select
 select += int(btnr(BUTTON.DOWN)) - int(btnr(BUTTON.UP))
 select = max(0, min(select, len(entries) - 1))
 if select != sp:
  pass
  # play sound here

 if btnr(BUTTON.ACCEPT) and entries:
  # play sound here
  selected_entry = entries[select]
  if selected_entry in ls_dir:
   path = link(path, selected_entry)
   load_directory()
  elif selected_entry in ls_file:
   # play sound here
   run(link(path, selected_entry))
 elif btnr(BUTTON.CANCEL):
  # play sound here
  split = path.strip("/").split("/")
  if split:
   split.pop()
  path = "/" + "/".join(split) if split else "/"
  load_directory()

def draw():
 cls()
 rect(0, 0, VIDEO.W, 8, COLOR.DARK_BLUE, 1)
 text(0, 0, path, COLOR.BLUE)
 for i, entry in enumerate(entries):
  is_dir = entry in ls_dir
  if i == select:
   rect(0, 8 + i * 8, VIDEO.W, 8, COLOR.DARK_GRAY, 1)
   text(0, 8 + i * 8, entry, COLOR.YELLOW if is_dir else COLOR.WHITE)
  else:
   text(0, 8 + i * 8, entry, COLOR.PINK if is_dir else COLOR.GRAY)
