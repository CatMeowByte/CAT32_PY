import time

def get_epoch():
 return int(time.time())

def get_time(utc=False):
 t = time.gmtime() if utc else time.localtime()
 return Box(
  year=t[0],
  month=t[1],
  day=t[2],
  hour=t[3],
  minute=t[4],
  second=t[5],
  weekday=t[6],
  yearday=t[7],
 )
