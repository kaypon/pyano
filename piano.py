import pygame
import numpy as np

# ─── Audio setup ───────────────────────────────────────────────────────────────
SAMPLE_RATE = 44100
DURATION    = 0.5  # seconds

# Convert MIDI note to frequency
def midi_to_freq(m):
    return 440.0 * 2 ** ((m - 69) / 12)

# ─── Notes for one octave ──────────────────────────────────────────────────────
white_notes = [
    ("C4", 60),
    ("D4", 62),
    ("E4", 64),
    ("F4", 65),
    ("G4", 67),
    ("A4", 69),
    ("B4", 71),
]

black_notes = {
    "C#4": (61, 0),
    "D#4": (63, 1),
    "F#4": (66, 3),
    "G#4": (68, 4),
    "A#4": (70, 5),
}

# ─── Key bindings ──────────────────────────────────────────────────────────────
# QWERTY row shortcuts
key_bindings = {
    pygame.K_z: "C4",
    pygame.K_s: "C#4",
    pygame.K_x: "D4",
    pygame.K_d: "D#4",
    pygame.K_c: "E4",
    pygame.K_v: "F4",
    pygame.K_g: "F#4",
    pygame.K_b: "G4",
    pygame.K_h: "G#4",
    pygame.K_n: "A4",
    pygame.K_j: "A#4",
    pygame.K_m: "B4",
}
# Invert for display
note_to_key = {note: pygame.key.name(k).upper() for k, note in key_bindings.items()}

# ─── Initialize pygame & pre-generate sounds ───────────────────────────────────
pygame.mixer.pre_init(frequency=SAMPLE_RATE, size=-16, channels=1)
pygame.init()

# Prepare sound buffers
t = np.linspace(0, DURATION, int(SAMPLE_RATE * DURATION), False)
sounds = {}
for name, midi in white_notes:
    wave = np.sin(2 * np.pi * midi_to_freq(midi) * t)
    audio = (wave * 32767).astype(np.int16)
    sounds[name] = pygame.sndarray.make_sound(audio)
for name, (midi, _) in black_notes.items():
    wave = np.sin(2 * np.pi * midi_to_freq(midi) * t)
    audio = (wave * 32767).astype(np.int16)
    sounds[name] = pygame.sndarray.make_sound(audio)

# ─── GUI setup ─────────────────────────────────────────────────────────────────
W, H = 80, 300  # key size
bw, bh = int(W * 0.6), int(H * 0.6)  # black key size
width = W * len(white_notes)
screen = pygame.display.set_mode((width, H))
pygame.display.set_caption("One-Octave Pygame Piano")
font = pygame.font.Font(None, 24)
small_font = pygame.font.Font(None, 18)

# track pressed keys for keyboard and mouse
pressed_keys = set()
pressed_mouse = set()
running = True
while running:
    screen.fill((180, 180, 180))

    # combine for highlighting
    pressed = pressed_keys | pressed_mouse

    # draw white keys with labels
    for i, (note, _) in enumerate(white_notes):
        rect = pygame.Rect(i * W, 0, W, H)
        color = (255, 230, 150) if note in pressed else (255, 255, 255)
        pygame.draw.rect(screen, color, rect)
        pygame.draw.rect(screen, (0, 0, 0), rect, 2)
        # draw note name at top
        txt = font.render(note, True, (0, 0, 0))
        txt_rect = txt.get_rect(center=(i * W + W/2, 20))
        screen.blit(txt, txt_rect)
        # draw shortcut at bottom
        key_label = note_to_key.get(note, "")
        sk = small_font.render(key_label, True, (0, 0, 0))
        sk_rect = sk.get_rect(center=(i * W + W/2, H - 20))
        screen.blit(sk, sk_rect)

    # draw black keys with labels
    for note, (_, idx) in black_notes.items():
        x = (idx + 1) * W - bw // 2
        rect = pygame.Rect(x, 0, bw, bh)
        color = (100, 100, 100) if note in pressed else (0, 0, 0)
        pygame.draw.rect(screen, color, rect)
        # draw note name
        txt = font.render(note.replace('#', '♯'), True, (255, 255, 255))
        txt_rect = txt.get_rect(center=(x + bw/2, 20))
        screen.blit(txt, txt_rect)
        # draw shortcut
        key_label = note_to_key.get(note, "")
        sk = small_font.render(key_label, True, (255, 255, 255))
        sk_rect = sk.get_rect(center=(x + bw/2, bh - 20))
        screen.blit(sk, sk_rect)

    pygame.display.flip()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        # keyboard press
        elif event.type == pygame.KEYDOWN:
            note = key_bindings.get(event.key)
            if note and note not in pressed_keys:
                sounds[note].play(-1)  # loop until stopped
                pressed_keys.add(note)

        elif event.type == pygame.KEYUP:
            note = key_bindings.get(event.key)
            if note and note in pressed_keys:
                sounds[note].stop()
                pressed_keys.remove(note)

        # mouse press
        elif event.type == pygame.MOUSEBUTTONDOWN:
            x, y = event.pos
            # black first
            for note, (_, idx) in black_notes.items():
                r = pygame.Rect((idx+1)*W - bw//2, 0, bw, bh)
                if r.collidepoint(x, y):
                    if note not in pressed_mouse:
                        sounds[note].play(-1)
                        pressed_mouse.add(note)
                    break
            else:
                w = x // W
                if 0 <= w < len(white_notes):
                    note = white_notes[w][0]
                    if note not in pressed_mouse:
                        sounds[note].play(-1)
                        pressed_mouse.add(note)

        # mouse release
        elif event.type == pygame.MOUSEBUTTONUP:
            for note in list(pressed_mouse):
                sounds[note].stop()
            pressed_mouse.clear()

pygame.quit()
