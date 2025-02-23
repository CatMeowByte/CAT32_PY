MAX_PROCESSES = 4
BANKS = [
 "_sprite_",
 "_layout_",
 "_tracks_",
]
LAUNCHER = "/app/file_explorer.app"

# Loop
GLOBAL.PROCESS = None # Reference of current iterated process

async def asyncio_tick():
 f = PROCESSES_FIELDS.tick
 while True:
  BUTTON._update_state()
  for pid, upref in enumerate(processes_upref.tick):
   if not upref: continue
   GLOBAL.PROCESS = processes[pid]
   try:
    upref()
   except Exception as e:
    _exception_error(e, pid, f.label)
    kill(pid)
    print(f"process {pid} killed")
  await asyncio.sleep(f.interval)

async def asyncio_draw():
 f = PROCESSES_FIELDS.draw
 while True:
  for pid, upref in enumerate(processes_upref.draw):
   if not upref: continue
   GLOBAL.PROCESS = processes[pid]
   mem(0)
   try:
    upref()
   except Exception as e:
    _exception_error(e, pid, f.label)
    kill(pid)
    print(f"process {pid} killed")
  VIDEO.flip()
  await asyncio.sleep(f.interval)

def generate_asyncio_periodic(field):
 f = PROCESSES_FIELDS[field]
 async def periodic_task():
  pid = 0
  while True:
   upref = processes_upref[field][pid]
   if upref:
    GLOBAL.PROCESS = processes[pid]
    try:
     upref()
    except Exception as e:
     _exception_error(e, pid, f.label)
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
   for field in PROCESSES_FIELDS
   if field.startswith("period_")
  )
 )

asyncio.run(asyncio_collection())