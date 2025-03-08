import sdl2

# Dependencies
COLOR = None
FONT = None
def depends(**kwargs): globals().update(kwargs)

SCALE = 2
SIZE = Box(
 W = 120,
 H = 0,
 HVIEW = 120,
 HBAR = 20,
 HFULL = 160,
)
MEM_VIEW = 0
MEM_TOP = 1
MEM_BOT = 2

renderer = None
texture = None
buffer = bytearray([0x00] * (SIZE.W * (SIZE.HBAR + SIZE.HVIEW // 2)))
mem = bytearray()
mem_top = memoryview(buffer)[0:(SIZE.W * SIZE.HBAR) // 2]
mem_view = memoryview(buffer)[(SIZE.W * SIZE.HBAR) // 2:(SIZE.W * (SIZE.HBAR + SIZE.HVIEW)) // 2]
mem_bot = memoryview(buffer)[(SIZE.W * (SIZE.HBAR + SIZE.HVIEW)) // 2:]
cam = Box(
 x = 0,
 y = 0,
)
text_wrap = False

def init():
 global renderer, texture, mem_top, mem_view, mem_bot, sprite

 if sdl2.SDL_Init(sdl2.SDL_INIT_VIDEO) != 0:
  raise Exception(f"SDL2 Initialization Error: {sdl2.SDL_GetError().decode()}")

 window = sdl2.SDL_CreateWindow(
  b"CAT32 Python",
  sdl2.SDL_WINDOWPOS_CENTERED,
  sdl2.SDL_WINDOWPOS_CENTERED,
  SIZE.W * SCALE,
  SIZE.HFULL * SCALE,
  sdl2.SDL_WINDOW_SHOWN
 )

 renderer = sdl2.SDL_CreateRenderer(window, -1, sdl2.SDL_RENDERER_ACCELERATED)
 sdl2.SDL_SetHint(sdl2.SDL_HINT_RENDER_SCALE_QUALITY, b"0")

 texture = sdl2.SDL_CreateTexture(
  renderer,
  sdl2.SDL_PIXELFORMAT_RGBA8888,
  sdl2.SDL_TEXTUREACCESS_STREAMING,
  SIZE.W,
  SIZE.HFULL
 )

 memsel()

def memsel(index=MEM_VIEW):
 global mem, SIZE, cam

 cam.x, cam.y = 0, 0

 if index == MEM_VIEW:
  mem = mem_view
  SIZE.H = SIZE.HVIEW
 elif index == MEM_TOP:
  mem = mem_top
  SIZE.H = SIZE.HBAR
 else:
  mem = mem_bot
  SIZE.H = SIZE.HBAR

def camera(x=0, y=0):
 global cam
 prev = (cam.x, cam.y)
 cam.x, cam.y = x, y
 return prev

def pixel_get(x, y):
 x = int(x)
 y = int(y)

 if x < 0 or x >= SIZE.W or y < 0 or y >= SIZE.H:
  return -1
 index = (y * SIZE.W + x) // 2
 return (mem[index] >> 4) if x % 2 == 0 else (mem[index] & 0x0F)

def pixel_set(x, y, color):
 x = int(x)
 y = int(y)
 color = int(color)

 if x < 0 or x >= SIZE.W or y < 0 or y >= SIZE.H:
  return
 if (COLOR.mask.bit & (1 << color)) != 0:
  return
 index = (y * SIZE.W + x) // 2
 is_hnibble = x % 2 == 0
 mem[index] = (
  (mem[index] & (0x0F if is_hnibble else 0xF0))
  | ((color & 0x0F) << (4 if is_hnibble else 0))
 )

def pixel(x, y, color=-1):
 x -= cam.x
 y -= cam.y
 if x < 0 or x >= SIZE.W or y < 0 or y >= SIZE.H:
  return -1

 old_color = pixel_get(x, y)

 if color != -1:
  pixel_set(x, y, color)

 return old_color

def line(x1, y1, x2, y2, color):
 x1 -= cam.x
 y1 -= cam.y
 x2 -= cam.x
 y2 -= cam.y

 dx = abs(x2 - x1)
 dy = abs(y2 - y1)
 sx = 1 if x1 < x2 else -1
 sy = 1 if y1 < y2 else -1
 err = dx - dy

 while True:
  pixel_set(x1, y1, color)

  if x1 == x2 and y1 == y2:
   break

  e2 = err * 2
  if e2 > -dy:
   err -= dy
   x1 += sx
  if e2 < dx:
   err += dx
   y1 += sy

def rect(x, y, width, height, color, fill=False):
 x = int(x)
 y = int(y)
 width = int(width)
 height = int(height)
 color = int(color)
 fill = bool(fill)

 x -= cam.x
 y -= cam.y
 if x >= SIZE.W or y >= SIZE.H or x + width <= 0 or y + height <= 0:
  return

 x_start = int(max(0, x))
 x_end = int(min(SIZE.W, x + width))
 y_start = int(max(0, y))
 y_end = int(min(SIZE.H, y + height))

 if fill:
  for scan_y in range(y_start, y_end):
   for scan_x in range(x_start, x_end):
    pixel_set(scan_x, scan_y, color)
 else:
  for scan_x in range(x_start, x_end):
   pixel_set(scan_x, y_start, color) # Top
   pixel_set(scan_x, y_end - 1, color) # Bottom

  for scan_y in range(y_start + 1, y_end - 1):
   pixel_set(x_start, scan_y, color) # Left
   pixel_set(x_end - 1, scan_y, color) # Right

def text(x, y, string, color, background=0):
 font_h = FONT.H
 font_w = FONT.W
 size_w = SIZE.W
 size_h = SIZE.H

 x -= cam.x
 y -= cam.y
 current_x = x
 current_y = y

 for ch in string:
  if ch == "\n":
   current_x = x
   current_y += font_h
   continue

  if text_wrap:
   if current_x >= size_w:
    if ch == " ":
     continue
    current_x = x
    current_y += font_h

  if current_x < -font_w or current_x >= size_w or current_y < -font_h or current_y >= size_h:
   current_x += font_w
   continue

  bits = FONT.CHAR.get(ord(ch), 0)
  for py in range(font_h):
   for px in range(font_w):
    on = (bits >> (py * font_w + px)) & 1
    tx = current_x + px
    ty = current_y + py
    if tx < 0 or tx >= size_w or ty < 0 or ty >= size_h:
     continue
    pixel_set(tx, ty, color if on else background)

  current_x += font_w

def blit_extended(
 src,
 src_size_w, src_size_h,
 src_x, src_y, src_w, src_h,
 dest_size_w, dest_size_h,
 dest_x, dest_y, dest_w, dest_h,
 rotation=0
):
 dest_x -= cam.x
 dest_y -= cam.y

 flip_h = dest_w < 0
 flip_v = dest_h < 0

 dest_w = int(abs(dest_w))
 dest_h = int(abs(dest_h))

 scale_x = float(src_w) / float(dest_w)
 scale_y = float(src_h) / float(dest_h)

 for y in range(dest_h):
  if dest_y + y < 0 or dest_y + y >= dest_size_h:
   continue

  for x in range(dest_w):
   if dest_x + x < 0 or dest_x + x >= dest_size_w:
    continue

   rotation = int(rotation)
   if rotation == 0:
    sx = int(src_x + (src_w - 1 - x * scale_x) if flip_h else src_x + x * scale_x)
    sy = int(src_y + (src_h - 1 - y * scale_y) if flip_v else src_y + y * scale_y)
   elif rotation == 1:
    sx = int(src_x + (src_h - 1 - y * scale_y) if not flip_v else src_x + y * scale_y)
    sy = int(src_y + (src_w - 1 - x * scale_x) if flip_h else src_y + x * scale_x)
   elif rotation == 2:
    sx = int(src_x + (src_w - 1 - x * scale_x) if not flip_h else src_x + x * scale_x)
    sy = int(src_y + (src_h - 1 - y * scale_y) if not flip_v else src_y + y * scale_y)
   elif rotation == 3:
    sx = int(src_x + (src_h - 1 - y * scale_y) if flip_v else src_x + y * scale_y)
    sy = int(src_y + (src_w - 1 - x * scale_x) if not flip_h else src_y + x * scale_x)

   if sx < 0 or sx >= src_size_w or sy < 0 or sy >= src_size_h:
    continue

   i = (sy * src_size_w + sx) // 2

   if i < 0 or i >= len(src):
    continue

   color = (src[i] >> 4) if sx % 2 == 0 else (src[i] & 0x0F)

   pixel_set(dest_x + x, dest_y + y, color)

def blit(
 src_x, src_y, src_w, src_h,
 dest_x, dest_y, dest_w, dest_h,
 rotation=0
):
 size = 128 if GLOBAL.PROCESS._pid_ == 0 else 64
 blit_extended(
  GLOBAL.PROCESS._sprite_,
  size, size,
  src_x, src_y, src_w, src_h,
  SIZE.W, SIZE.HFULL,
  dest_x, dest_y, dest_w, dest_h,
  rotation
 )

def clear(color=0):
 mem[:] = bytes([((color & 0x0F) << 4) | (color & 0x0F)] * len(mem))

import time
if GLOBAL.MICROPYTHON:
 get_time = time.ticks_ms
 time_diff = time.ticks_diff
else:
 get_time = lambda: int(time.time() * 1000)  # Convert seconds to ms
 time_diff = lambda a, b: a - b  # Simple subtraction

t = get_time()

def flip():
 global t
 size_w = SIZE.W
 size_hfull = SIZE.HFULL
 color_palette = COLOR.PALETTE

 # Ticker
 now = get_time()
 memsel(2)
 text(size_w / 2 - 10, 12, f"{1000 / (time_diff(now, t) or 1):05.2f}", COLOR.DARK_BLUE, COLOR.WHITE)
 t = now

 pixels = bytearray(size_w * size_hfull * 4)
 for y in range(size_hfull):
  for x in range(size_w):
   offset = y * size_w + x
   memory_byte = buffer[offset // 2]
   color_index = (memory_byte >> 4) if x % 2 == 0 else (memory_byte & 0x0F)
   pixel_index = offset * 4
   r, g, b = color_palette[color_index]
   pixels[pixel_index] = 255
   pixels[pixel_index + 1] = b
   pixels[pixel_index + 2] = g
   pixels[pixel_index + 3] = r

 sdl2.SDL_UpdateTexture(texture, None, bytes(pixels), size_w * 4)
 sdl2.SDL_RenderCopy(renderer, texture, None, None)
 sdl2.SDL_RenderPresent(renderer)
