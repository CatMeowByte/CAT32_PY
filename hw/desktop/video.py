import math
import sdl2

# TODO: convert to async

SCALE = 3
W = 120
HVIEW = 120
HBAR = 20
MEM_VIEW = 0
MEM_TOP = 1
MEM_BOT = 2

renderer = None
texture = None
mem = bytearray()
H = 0
mem_top = bytearray()
mem_view = bytearray()
mem_bot = bytearray()
cam = [0, 0]
text_wrap = False

def init():
 global renderer, texture, mem_top, mem_view, mem_bot, sprite

 if sdl2.SDL_Init(sdl2.SDL_INIT_VIDEO) != 0:
  raise Exception(f"SDL2 Initialization Error: {sdl2.SDL_GetError().decode()}")

 window = sdl2.SDL_CreateWindow(
  b"CAT32 Python",
  sdl2.SDL_WINDOWPOS_CENTERED,
  sdl2.SDL_WINDOWPOS_CENTERED,
  W * SCALE,
  (HBAR + HVIEW + HBAR) * SCALE,
  sdl2.SDL_WINDOW_SHOWN
 )

 renderer = sdl2.SDL_CreateRenderer(window, -1, sdl2.SDL_RENDERER_ACCELERATED)
 sdl2.SDL_SetHint(sdl2.SDL_HINT_RENDER_SCALE_QUALITY, b"0")

 texture = sdl2.SDL_CreateTexture(
  renderer,
  sdl2.SDL_PIXELFORMAT_RGBA8888,
  sdl2.SDL_TEXTUREACCESS_STREAMING,
  W,
  HBAR + HVIEW + HBAR
 )

 mem_top = bytearray((W * HBAR) // 2)
 mem_view = bytearray((W * HVIEW) // 2)
 mem_bot = bytearray((W * HBAR) // 2)

 mem_top[:] = [0] * len(mem_top)
 mem_view[:] = [0] * len(mem_view)
 mem_bot[:] = [0] * len(mem_bot)

 memsel()

def memsel(id=MEM_VIEW):
 global mem, H, cam

 cam = [0, 0]

 if id == MEM_VIEW:
  mem = mem_view
  H = HVIEW
 elif id == MEM_TOP:
  mem = mem_top
  H = HBAR
 else:
  mem = mem_bot
  H = HBAR

def camera(x=0, y=0):
 global cam
 prev = cam[:]
 cam = [x, y]
 return prev

def _pixel_get(x, y):
 x = int(x)
 y = int(y)

 if x < 0 or x >= W or y < 0 or y >= H:
  return -1
 index = (y * W + x) // 2
 return (mem[index] >> 4) if x % 2 == 0 else (mem[index] & 0x0F)

def _pixel_set(x, y, color):
 x = int(x)
 y = int(y)
 color = int(color)

 if x < 0 or x >= W or y < 0 or y >= H:
  return
 if (COLOR.mask & (1 << color)) != 0:
  return
 index = (y * W + x) // 2
 is_hnibble = x % 2 == 0
 mem[index] = (
  (mem[index] & (0x0F if is_hnibble else 0xF0))
  | ((color & 0x0F) << (4 if is_hnibble else 0))
 )

def pixel(x, y, color=-1):
 x -= cam[0]
 y -= cam[1]
 if x < 0 or x >= W or y < 0 or y >= H:
  return -1

 old_color = _pixel_get(x, y)

 if color != -1:
  _pixel_set(x, y, color)

 return old_color

def line(x1, y1, x2, y2, color):
 x1 -= cam[0]
 y1 -= cam[1]
 x2 -= cam[0]
 y2 -= cam[1]

 dx = abs(x2 - x1)
 dy = abs(y2 - y1)
 sx = 1 if x1 < x2 else -1
 sy = 1 if y1 < y2 else -1
 err = dx - dy

 while True:
  _pixel_set(x1, y1, color)

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

 x -= cam[0]
 y -= cam[1]
 if x >= W or y >= H or x + width <= 0 or y + height <= 0:
  return

 x_start = int(max(0, x))
 x_end = int(min(W, x + width))
 y_start = int(max(0, y))
 y_end = int(min(H, y + height))

 if fill:
  for scan_y in range(y_start, y_end):
   for scan_x in range(x_start, x_end):
    _pixel_set(scan_x, scan_y, color)
 else:
  for scan_x in range(x_start, x_end):
   _pixel_set(scan_x, y_start, color) # Top
   _pixel_set(scan_x, y_end - 1, color) # Bottom

  for scan_y in range(y_start + 1, y_end - 1):
   _pixel_set(x_start, scan_y, color) # Left
   _pixel_set(x_end - 1, scan_y, color) # Right

def text(x, y, string, color, background=0):
 x -= cam[0]
 y -= cam[1]
 current_x = x
 current_y = y

 for ch in string:
  if ch == "\n": # Newline
   current_x = x
   current_y += FONT.H
   continue

  ordinal = ord(ch)

  # Wrapping
  if text_wrap:
   if current_x >= W:
    if ch == " ": # Space
     continue
    current_x = x
    current_y += FONT.H

  character(current_x, current_y, ordinal, color, background)
  current_x += FONT.W


def character(x, y, ordinal, color, background=0):
 if x < -FONT.W or x >= W or y < -FONT.H or y >= H:
  return

 bits = FONT.CHAR.get(ordinal, 0)
 for py in range(FONT.H):
  for px in range(FONT.W):
   on = (bits >> (py * FONT.W + px)) & 1
   tx = x + px
   ty = y + py
   if tx < 0 or tx >= W or ty < 0 or ty >= H:
    continue
   _pixel_set(tx, ty, color if on else background)

def blit_source_to_dest(
 src,
 src_size_w, src_size_h,
 src_x, src_y, src_w, src_h,
 dest_size_w, dest_size_h,
 dest_x, dest_y, dest_w, dest_h,
 rotation=0
):
 dest_x -= cam[0]
 dest_y -= cam[1]

 flip_h = dest_w < 0
 flip_v = dest_h < 0

 dest_w = abs(dest_w)
 dest_h = abs(dest_h)

 scale_x = float(src_w) / float(dest_w)
 scale_y = float(src_h) / float(dest_h)

 for y in range(dest_h):
  if dest_y + y < 0 or dest_y + y >= dest_size_h:
   continue

  for x in range(dest_w):
   if dest_x + x < 0 or dest_x + x >= dest_size_w:
    continue

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

   _pixel_set(dest_x + x, dest_y + y, color)

def blit(
 src_x, src_y, src_w, src_h,
 dest_size_w, dest_size_h,
 dest_x, dest_y, dest_w, dest_h,
 rotation=0
):
 size = int(math.sqrt(len(__sprite__) / 2))
 blit_source_to_dest(
  __sprite__,
  size, size,
  src_x, src_y, src_w, src_h,
  dest_size_w, dest_size_h,
  dest_x, dest_y, dest_w, dest_h,
  rotation=0
 )

def clear(color=0):
 mem[:] = [((color & 0x0F) << 4) | (color & 0x0F)] * len(mem)

def flip():
 pixels = bytearray(W * (HBAR + HVIEW + HBAR) * 4)
 for y in range(HBAR + HVIEW + HBAR):
  if y < HBAR:
   buffer = mem_top
   oy = y
  elif y < HBAR + HVIEW:
   buffer = mem_view
   oy = y - HBAR
  else:
   buffer = mem_bot
   oy = y - HBAR - HVIEW

  for x in range(W):
   memory_byte = buffer[(oy * W + x) // 2]
   color_index = (memory_byte >> 4) if x % 2 == 0 else (memory_byte & 0x0F)
   pixel_index = (y * W + x) * 4
   r, g, b = COLOR.PALETTE[color_index]
   pixels[pixel_index] = 255
   pixels[pixel_index + 1] = b
   pixels[pixel_index + 2] = g
   pixels[pixel_index + 3] = r

 sdl2.SDL_UpdateTexture(texture, None, bytes(pixels), W * 4)
 sdl2.SDL_RenderCopy(renderer, texture, None, None)
 sdl2.SDL_RenderPresent(renderer)
