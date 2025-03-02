import asyncio
import os

MAX_PROCESSES = 4
BANKS = (
 "_sprite_",
 "_layout_",
 "_tracks_",
)
LAUNCHER = "/app/file_explorer.app"

def exception_error(e, pid, at):
 error_type = type(e).__name__
 error_message = str(e)
 tb = e.__traceback__
 while tb.tb_next:
  tb = tb.tb_next
 line_number = tb.tb_lineno

 print(f"[{at} ERROR]")
 print(f"{processes[pid]._filename_}:{line_number}")
 print(f"{error_type}:")
 print(error_message)

# Process
processes_fields = Box(
 tick=Box(label="UPDATE", interval=1/GLOBAL.TICK),
 draw=Box(label="DRAW", interval=1/GLOBAL.TICK),
 period_q=Box(label="PERIOD QUARTER SECOND", interval=1/4),
 period_h=Box(label="PERIOD HALF SECOND", interval=1/2),
)
for secs in (1, 2, 4, 8, 16, 32):
 processes_fields[f"period_{secs}"] = Box(label=f"PERIOD {secs} SECOND", interval=secs)

processes_event_ref = Box()
for field in processes_fields:
 processes_event_ref[field] = [None] * MAX_PROCESSES

processes = [None] * MAX_PROCESSES

def kill(pid):
 for field in processes_event_ref:
  processes_event_ref[field][pid] = None
 processes[pid] = None

def run(script, pid=0):
 pid = clamp(pid, 0, MAX_PROCESSES - 1)
 kill(pid)
 obj, obj_space = type("", (), {})(), Box()
 path = link(GLOBAL.ROOT, script)
 obj_space._filename_ = path.rsplit("/", 1)[-1]
 obj_space._pid_ = pid
 obj_space.GLOBAL = GLOBAL
 obj_space.update(GLOBAL.STATIC)
 lines = None
 with open(path, "r") as f: lines = f.readlines()
 for line in lines:
  for bank in BANKS:
   if line.startswith(bank): exec(line, obj_space)
 try:
  exec("".join(lines), obj_space)
 except Exception as e:
  exception_error(e, pid, "LOAD")
  kill(pid)
  print(f"process {pid} killed")

 for k, v in obj_space.items(): setattr(obj, k, v)
 processes[pid] = obj

 for field in processes_fields:
  attr = "update" if field == "tick" else field # Exception
  processes_event_ref[field][pid] = getattr(processes[pid], attr, None)

 # Init
 try:
  processes[pid].init()
 except AttributeError: pass
 except Exception as e:
  exception_error(e, pid, "INIT")
  kill(pid)
  print(f"process {pid} killed")

def exit_to_menu():
 run(LAUNCHER)

make_static(
 kill = kill,
 run = run,
 exit_to_menu = exit_to_menu,
)

@oneshot
def load_services():
 services = []
 for file in os.listdir(link(GLOBAL.ROOT, "svc")):
  if file.endswith(".svc"):
   services.append(file)

 for i, service in enumerate(services):
  if i < MAX_PROCESSES - 1:
   run(link("svc", service), i + 1)

run(LAUNCHER)

# Loop
GLOBAL.PROCESS = None # Reference of current iterated process

async def asyncio_tick():
 f = processes_fields.tick
 while True:
  BUTTON._update_state()
  for pid, upref in enumerate(processes_event_ref.tick):
   if not upref: continue
   GLOBAL.PROCESS = processes[pid]
   try:
    upref()
   except Exception as e:
    exception_error(e, pid, f.label)
    kill(pid)
    print(f"process {pid} killed")
  await asyncio.sleep(f.interval)

async def asyncio_draw():
 f = processes_fields.draw
 while True:
  for pid, upref in enumerate(processes_event_ref.draw):
   if not upref: continue
   GLOBAL.PROCESS = processes[pid]
   mem(0)
   try:
    upref()
   except Exception as e:
    exception_error(e, pid, f.label)
    kill(pid)
    print(f"process {pid} killed")
  VIDEO.flip()
  await asyncio.sleep(f.interval)

def generate_asyncio_periodic(field):
 f = processes_fields[field]
 async def periodic_task():
  pid = 0
  while True:
   upref = processes_event_ref[field][pid]
   if upref:
    GLOBAL.PROCESS = processes[pid]
    try:
     upref()
    except Exception as e:
     exception_error(e, pid, f.label)
     kill(pid)
     print(f"process {pid} killed")
   await asyncio.sleep(f.interval / MAX_PROCESSES)
   pid = (pid + 1) % MAX_PROCESSES
 return periodic_task

async def asyncio_collection():
 await asyncio.gather(
  asyncio_tick(),
  asyncio_draw(),
  *(
   generate_asyncio_periodic(field)()
   for field in processes_fields
   if field.startswith("period_")
  )
 )

asyncio.run(asyncio_collection())