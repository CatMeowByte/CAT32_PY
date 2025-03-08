def tick():
 if btnr(BUTTON.CANCEL):
  exit_to_menu()

def draw():
 cls(COLOR.DARK_BLUE)
 line(0, 0, 120, 120, COLOR.WHITE)
 text(8, 16, "Hi, all!", COLOR.YELLOW)
 text(0, VIDEO.SIZE.H - 8, str(BUTTON.state), COLOR.GRAY)
 pix(pos[0], pos[1], COLOR.PINK)