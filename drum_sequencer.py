import pygame
import numpy as np
import time

# ─── Enhanced Drum Step Sequencer ─────────────────────────────────────────────
# 4 instruments × 16 steps, Play/Stop, live BPM control, click to toggle steps

# Audio settings
SAMPLE_RATE = 44100

# Initial sequencer settings
BPM = 120
STEPS = 16
INSTRUMENTS = ["Kick", "Snare", "HiHat", "Clap"]
ROWS = len(INSTRUMENTS)
COLS = STEPS

# UI settings
CELL_W, CELL_H = 40, 40
PADDING = 2
GRID_W = CELL_W * COLS
GRID_H = CELL_H * ROWS
UI_H = GRID_H + 80  # extra space for controls
UI_W = GRID_W + 200  # extra for labels and controls

# Generate basic drum sounds via NumPy
def make_kick():
    t = np.linspace(0, 0.5, int(SAMPLE_RATE*0.5), False)
    freqs = np.linspace(150, 60, t.size)
    wave = np.sin(2*np.pi*freqs*t)
    env = np.exp(-t*8)
    samples = (wave*env*32767).astype(np.int16)
    return pygame.sndarray.make_sound(samples)

def make_snare():
    t = np.linspace(0, 0.3, int(SAMPLE_RATE*0.3), False)
    noise = np.random.randn(t.size)
    env = np.exp(-t*20)
    samples = (noise*env*32767).astype(np.int16)
    return pygame.sndarray.make_sound(samples)

def make_hihat():
    t = np.linspace(0, 0.1, int(SAMPLE_RATE*0.1), False)
    noise = np.random.randn(t.size)
    kernel = np.ones(30)/30
    lp = np.convolve(noise, kernel, mode='same')
    hp = noise - lp
    env = np.exp(-t*30)
    samples = (hp*env*32767).astype(np.int16)
    return pygame.sndarray.make_sound(samples)

def make_clap():
    t = np.linspace(0, 0.2, int(SAMPLE_RATE*0.2), False)
    noise = np.random.randn(t.size)
    env = np.exp(-t*15)
    samples = (noise*env*32767).astype(np.int16)
    return pygame.sndarray.make_sound(samples)

# Initialize Pygame
pygame.mixer.pre_init(SAMPLE_RATE, -16, 1)
pygame.init()

# Create display, font, and clock
screen = pygame.display.set_mode((UI_W, UI_H))
pygame.display.set_caption("Drum Step Sequencer")
font = pygame.font.Font(None, 24)
clock = pygame.time.Clock()

# Load sounds
sounds = [make_kick(), make_snare(), make_hihat(), make_clap()]

# Sequencer state
pattern = [[False]*COLS for _ in range(ROWS)]
is_playing = False
current_step = 0
step_ms = 60000 // BPM // 4
last_step_time = pygame.time.get_ticks()

# Control buttons
play_btn = pygame.Rect(GRID_W + 20, 20, 80, 40)
stop_btn = pygame.Rect(GRID_W + 20, 70, 80, 40)
bpm_up = pygame.Rect(GRID_W + 120, 20, 40, 40)
bpm_dn = pygame.Rect(GRID_W + 120, 70, 40, 40)

running = True
while running:
    now = pygame.time.get_ticks()
    for e in pygame.event.get():
        if e.type == pygame.QUIT:
            running = False
        elif e.type == pygame.MOUSEBUTTONDOWN:
            x, y = e.pos
            # Toggle grid cells
            if y < GRID_H and x < GRID_W:
                col = x // CELL_W
                row = y // CELL_H
                pattern[row][col] = not pattern[row][col]
            # Play/Stop
            elif play_btn.collidepoint(x, y):
                is_playing = True
                current_step = 0
                last_step_time = now
            elif stop_btn.collidepoint(x, y):
                is_playing = False
            # BPM control
            elif bpm_up.collidepoint(x, y):
                BPM = min(300, BPM + 5)
                step_ms = 60000 // BPM // 4
            elif bpm_dn.collidepoint(x, y):
                BPM = max(30, BPM - 5)
                step_ms = 60000 // BPM // 4

    # Sequencer timing
    if is_playing and now - last_step_time >= step_ms:
        for r in range(ROWS):
            if pattern[r][current_step]:
                sounds[r].play()
        current_step = (current_step + 1) % COLS
        last_step_time += step_ms

    # Draw UI
    screen.fill((30, 30, 30))
    # Grid
    for r in range(ROWS):
        for c in range(COLS):
            rect = pygame.Rect(c*CELL_W, r*CELL_H, CELL_W - PADDING, CELL_H - PADDING)
            color = (200, 100, 100) if pattern[r][c] else (80, 80, 80)
            if is_playing and c == current_step:
                color = (250, 200, 100)
            pygame.draw.rect(screen, color, rect)
    # Instrument labels
    for i, name in enumerate(INSTRUMENTS):
        screen.blit(font.render(name, True, (200, 200, 200)), (GRID_W + 20, i*CELL_H + 5))
    # Buttons
    pygame.draw.rect(screen, (50, 200, 50), play_btn)
    screen.blit(font.render("Play", True, (0, 0, 0)), (play_btn.x + 10, play_btn.y + 10))
    pygame.draw.rect(screen, (200, 50, 50), stop_btn)
    screen.blit(font.render("Stop", True, (0, 0, 0)), (stop_btn.x + 10, stop_btn.y + 10))
    pygame.draw.rect(screen, (100, 100, 250), bpm_up)
    screen.blit(font.render("+", True, (255, 255, 255)), (bpm_up.x + 12, bpm_up.y + 5))
    pygame.draw.rect(screen, (100, 100, 250), bpm_dn)
    screen.blit(font.render("-", True, (255, 255, 255)), (bpm_dn.x + 14, bpm_dn.y + 5))
    # BPM display
    bpm_text = font.render(f"BPM: {BPM}", True, (255, 255, 255))
    screen.blit(bpm_text, (GRID_W + 20, 130))

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
