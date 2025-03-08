path = "/boot.py"

txt = []
crs = [0, 0]
scr_off = [0, 0]
scr_max = [0, 0]
scr_spd = 0.2

btn_d = 2
btn_i = 1

video_size = VIDEO.SIZE

with open(link(GLOBAL.ROOT, path), "r") as f:
 txt = f.readlines()

for ln in txt:
 scr_max[0] = max(scr_max[0], (len(ln) + 1) * 4 - video_size.W)

scr_max[1] = max(0, len(txt) * 8 - video_size.HVIEW)

def tick():
 dx = int(btnr(BUTTON.RIGHT, btn_d, btn_i)) - int(btnr(BUTTON.LEFT, btn_d, btn_i))
 dy = int(btnr(BUTTON.DOWN, btn_d, btn_i)) - int(btnr(BUTTON.UP, btn_d, btn_i))

 if btnr(BUTTON.CANCEL):
  exit_to_menu()

 crs[0] = clamp(crs[0] + dx, 0, (scr_max[0] + video_size.W) // 4 - 1)
 crs[1] = clamp(crs[1] + dy, 0, (scr_max[1] + video_size.HVIEW) // 8 - 1)

 scr_tx = crs[0] * 4 - video_size.W / 2 + 2
 scr_ty = crs[1] * 8 - video_size.HVIEW / 2 + 4

 scr_off[0] += (scr_tx - scr_off[0]) * scr_spd
 scr_off[1] += (scr_ty - scr_off[1]) * scr_spd

 scr_off[0] = clamp(scr_off[0], 0, scr_max[0])
 scr_off[1] = clamp(scr_off[1], 0, scr_max[1])

def draw():
 cls(COLOR.DARK_BLUE)
 cam(scr_off[0], scr_off[1])

 rect(crs[0] * 4, crs[1] * 8, 4, 8, COLOR.DARK_PURPLE, 1)
 line(crs[0] * 4, crs[1] * 8, crs[0] * 4, crs[1] * 8 + 7, COLOR.RED)

 for i in range(len(txt)):
  ln = txt[i]
  fg = COLOR.WHITE if i == crs[1] else COLOR.GRAY
  text(0, i * 8, ln, fg)