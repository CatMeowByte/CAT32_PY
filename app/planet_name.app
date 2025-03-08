VOWELS = ["a", "e", "i", "o", "u"]
CONSONANTS = ["b", "c", "d", "f", "g", "h", "j", "k", "l", "m", "n", "p", "q", "r", "s", "t", "v", "w", "x", "y", "z"]
WEIGHTED_CONSONANTS = ["z", "f", "q", "r", "x", "v"]
PREFIXES = [
 "exo", "astro", "terra", "nova", "inter", "neo", "stellar", "galacto", "cryo", "aero",
 "lumino", "chrono", "cyber", "quantum", "spectra", "hyper", "ultra", "electro", "mega", "sub",
 "astro", "exo", "macro", "nano", "psycho", "solar", "lunar", "plasma", "magno", "vortex",
 "proto", "infra", "extra", "radial", "holo", "geo", "bio", "anti", "micro", "meta"
]
SUFFIXES = [
 "xenia", "prime", "ion", "aria", "ium", "or", "tron", "os", "thia", "dax",
 "etis", "arix", "enix", "alor", "vium", "dora", "zor", "thar", "sion", "plex",
 "nium", "xar", "troid", "phor", "tica", "gen", "polis", "car", "gath", "zon",
 "core", "gate", "phy", "synth", "verse", "drone", "flux", "scope", "nova", "shade"
]

current_planet_name = ""

def generate_name():
 planet_name = ""
 len_cost = 12
 word_count = 0
 max_words = int(rnd(1, 4))

 while not planet_name:
  while word_count < max_words and len_cost > 0:
   if word_count == max_words - 1 and max_words > 1:
    codename = generate_random_codename()
    if codename["cost"] <= len_cost:
     planet_name += codename["word"]
     len_cost -= codename["cost"]
    else:
     break
   else:
    normal_word = generate_normal_word(len_cost)
    if normal_word["cost"] <= len_cost:
     planet_name += normal_word["word"]
     len_cost -= normal_word["cost"]
    else:
     break
   if word_count < max_words - 1 and len_cost > 0:
    planet_name += " "
   word_count += 1

  if word_count == 1 and len_cost > 0 and len(planet_name) < 6:
   filler = generate_normal_word(len_cost)
   planet_name += " " + filler["word"] if len(planet_name) > 0 else filler["word"]

 return planet_name

def generate_normal_word(len_cost):
 word = ""
 cost = 0

 if rnd() < 0.3 and len_cost > 3:
  prefix = PREFIXES[int(rnd(0, len(PREFIXES)))]
  word += prefix
  cost += len(prefix)

 core_length = max(2, min(len_cost - cost, int(rnd(2, 8))))
 use_vowel = False
 for i in range(core_length):
  if use_vowel:
   word += VOWELS[int(rnd(0, len(VOWELS)))]
  else:
   if rnd() < 0.3:
    word += WEIGHTED_CONSONANTS[int(rnd(0, len(WEIGHTED_CONSONANTS)))]
   else:
    word += CONSONANTS[int(rnd(0, len(CONSONANTS)))]
  use_vowel = not use_vowel
 cost += core_length

 if rnd() < 0.3 and len_cost - cost > 3:
  suffix = SUFFIXES[int(rnd(0, len(SUFFIXES)))]
  word += suffix
  cost += len(suffix)

 return {"word": word.capitalize(), "cost": cost}

def generate_codename_letter():
 word = ""
 core_length = max(2, int(rnd(2, 5)))
 use_vowel = False
 for i in range(core_length):
  if use_vowel:
   word += VOWELS[int(rnd(0, len(VOWELS)))]
  else:
   if rnd() < 0.3:
    word += WEIGHTED_CONSONANTS[int(rnd(0, len(WEIGHTED_CONSONANTS)))]
   else:
    word += CONSONANTS[int(rnd(0, len(CONSONANTS)))]
  use_vowel = not use_vowel
 return {"word": word.upper(), "cost": core_length}

# Generate key and number (e.g., ZOR-43)
def generate_codename_key():
 word = generate_codename_letter()["word"] + "-" + str(int(rnd(1, 99 + 1)))
 return {"word": word, "cost": 6}

# Generate letter + number (e.g., A328)
def generate_codename_keynum():
 word = CONSONANTS[int(rnd(0, len(CONSONANTS)))] .upper() + str(int(rnd(100, 999 + 1)))
 return {"word": word, "cost": 4}

# Generate numbers (e.g., 1985)
def generate_codename_order():
 word = str(int(rnd(10, 9999 + 1)))
 return {"word": word, "cost": 3}

def generate_random_codename():
 rand = rnd()
 if rand < 0.2:
  return generate_codename_letter()
 elif rand < 0.6:
  return generate_codename_key()
 elif rand < 0.8:
  return generate_codename_keynum()
 else:
  return generate_codename_order()

def tick():
 global current_planet_name
 if btnr(BUTTON.ACCEPT):
  current_planet_name = generate_name()
  print(current_planet_name)
 if btnr(BUTTON.CANCEL):
  exit_to_menu()

def draw():
 cls(COLOR.DARK_BLUE)
 text(0, 0, "Sci-Fi Planet Generator", COLOR.BLUE)
 cx = (VIDEO.SIZE.W - len(current_planet_name) * 4) / 2
 cy = (VIDEO.SIZE.H / 2) - 4
 mask(COLOR.BLACK, False)
 mask(COLOR.PINK, True)
 text(cx + 1, cy + 1, current_planet_name, COLOR.BLACK, COLOR.PINK)
 mask()
 text(cx, cy, current_planet_name, COLOR.WHITE)

 text(0, VIDEO.SIZE.H - 8, "Press ACCEPT to regenerate", COLOR.DARK_GRAY)
