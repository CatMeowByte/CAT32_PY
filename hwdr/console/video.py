import framebuf

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

buffer = bytearray(SIZE.W * (SIZE.HBAR + SIZE.HVIEW // 2))
fbuf = framebuf.FrameBuffer(buffer, SIZE.W, SIZE.H, framebuf.GS4_HMSB)
cam = Box(
 x = 0,
 y = 0,
)
text_wrap = False

# framebuf.GS4_HMSB