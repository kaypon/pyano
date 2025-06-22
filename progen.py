import pygame
import numpy as np
import random
import time

# ─── Procedural One-Octave Piano Generator with UI ────────────────────────────
# Plays a weighted random-walk melody over C4–B4 and highlights keys.

# Audio settings
SAMPLE_RATE = 44100
BUFFER_SEC = 1.0  # seconds for tone buffer

# MIDI to frequency conversion
def midi_to_freq(m):
    return 440.0 * 2 ** ((m - 69) / 12)

# Define one octave: C4–B4
white_notes = [
    ("C4", 60), ("D4", 62), ("E4", 64),
    ("F4", 65), ("G4", 67), ("A4", 69), ("B4", 71)
]
black_notes = {
    "C#4": (61, 0), "D#4": (63, 1),
    "F#4": (66, 3), "G#4": (68, 4), "A#4": (70, 5)
}

# Procedural parameters
tempo_bpm = 120
beat_duration = 60.0 / tempo_bpm
sequence_length = 64

# Weighted intervals and durations
step_weights = {-2: 1, -1: 5, 0: 2, 1: 5, 2: 1}
duration_weights = {0.5: 1, 1: 5, 1.5: 2, 2: 1}

# UI dimensions
W, H = 80, 300               # white key size
bw, bh = int(W * 0.6), int(H * 0.6)  # black key size

# Initialize Pygame
pygame.mixer.pre_init(SAMPLE_RATE, -16, 1)
pygame.init()

# Pre-generate tone buffers for each note
t_arr = np.linspace(0, BUFFER_SEC, int(SAMPLE_RATE * BUFFER_SEC), False)
tones = {}
for name, midi in white_notes + list(black_notes.items()):
    if isinstance(midi, tuple):
        midi = midi[0]
    wave_arr = np.sin(2 * np.pi * midi_to_freq(midi) * t_arr)
    audio = (wave_arr * 32767).astype(np.int16)
    tones[name] = pygame.sndarray.make_sound(audio)

# Setup display
num_white = len(white_notes)
width = W * num_white
screen = pygame.display.set_mode((width, H))
pygame.display.set_caption("Procedural Piano UI")
font = pygame.font.Font(None, 24)

# Helper to draw keys; highlight single note
def draw_keys(active_note=None):
    pygame.event.pump()
    screen.fill((50, 50, 50))
    # White keys
    for i, (name, _) in enumerate(white_notes):
        rect = pygame.Rect(i * W, 0, W, H)
        color = (180, 180, 255) if name == active_note else (255, 255, 255)
        pygame.draw.rect(screen, color, rect)
        pygame.draw.rect(screen, (0, 0, 0), rect, 2)
        screen.blit(font.render(name, True, (0, 0, 0)), (rect.x + 5, rect.y + 5))
    # Black keys
    for name, (_, idx) in black_notes.items():
        x = (idx + 1) * W - bw // 2
        rect = pygame.Rect(x, 0, bw, bh)
        color = (100, 100, 200) if name == active_note else (0, 0, 0)
        pygame.draw.rect(screen, color, rect)
        screen.blit(font.render(name.replace('#', '♯'), True, (255, 255, 255)), (rect.x + 5, rect.y + 5))
    pygame.display.flip()

# Initial draw
draw_keys()

# Melody playback state
current_idx = len(white_notes) // 2  # start at middle white key
for _ in range(sequence_length):
    # Weighted random step on white notes
    steps, weights = zip(*step_weights.items())
    step = random.choices(steps, weights=weights)[0]
    current_idx = max(0, min(len(white_notes) - 1, current_idx + step))
    note_name, _ = white_notes[current_idx]

    # Weighted random duration
    durs, dws = zip(*duration_weights.items())
    beats = random.choices(durs, weights=dws)[0]
    duration = beats * beat_duration

    # Play and highlight
    tone = tones[note_name]
    tone.play(-1)
    draw_keys(active_note=note_name)
    time.sleep(duration)
    tone.stop()
    draw_keys(active_note=None)

pygame.quit()
