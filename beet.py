import pygame
import numpy as np
import sounddevice as sd

# ─── Live Voice Sampler Pad with Key Controls (beet.py) ────────────────────────
# 2×4 pads: hold left-click or number key to record/play; right-click to delete.

# Audio settings
SAMPLE_RATE = 44100
CHANNELS = 1

# Pad grid configuration
PAD_ROWS, PAD_COLS = 2, 4
PAD_W, PAD_H = 100, 100
PADDING = 10

grid_w = PAD_COLS * PAD_W + (PAD_COLS + 1) * PADDING
grid_h = PAD_ROWS * PAD_H + (PAD_ROWS + 1) * PADDING
UI_W, UI_H = grid_w, grid_h + 60

# Initialize Pygame mixer & display
pygame.mixer.pre_init(SAMPLE_RATE, -16, CHANNELS)
pygame.init()
screen = pygame.display.set_mode((UI_W, UI_H))
pygame.display.set_caption("beet.py - Voice Sampler Pad")
font = pygame.font.Font(None, 36)

# Pad state
dpads = {}          # pad_id -> pygame.mixer.Sound
is_playing = {}     # pad_id -> bool

# Recording state
recording_pad = None
recorded_chunks = []

# Audio callback to capture microphone input
def audio_callback(indata, frames, time, status):
    if recording_pad is not None:
        recorded_chunks.append(indata.copy())

# Start input stream
stream = sd.InputStream(samplerate=SAMPLE_RATE, channels=CHANNELS, callback=audio_callback)
stream.start()

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        # Mouse events
        elif event.type == pygame.MOUSEBUTTONDOWN:
            mx, my = event.pos
            for r in range(PAD_ROWS):
                for c in range(PAD_COLS):
                    pad_id = r * PAD_COLS + c
                    x = PADDING + c * (PAD_W + PADDING)
                    y = PADDING + r * (PAD_H + PADDING)
                    rect = pygame.Rect(x, y, PAD_W, PAD_H)
                    if rect.collidepoint(mx, my):
                        if event.button == 1:  # left click
                            if dpads.get(pad_id) is None:
                                # start recording into this pad
                                recording_pad = pad_id
                                recorded_chunks = []
                            else:
                                # start playback on hold
                                dpads[pad_id].play(loops=-1)
                                is_playing[pad_id] = True
                        elif event.button == 3 and dpads.get(pad_id):  # right click
                            # delete pad
                            dpads.pop(pad_id)
                            is_playing.pop(pad_id, None)
                        break

        # Mouse button up: stop recording or playback
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                if recording_pad is not None:
                    # finish recording
                    data = np.concatenate(recorded_chunks, axis=0).flatten()
                    data *= 32767 / np.max(np.abs(data))
                    audio = data.astype(np.int16)
                    snd = pygame.sndarray.make_sound(audio)
                    dpads[recording_pad] = snd
                    is_playing[recording_pad] = False
                    recording_pad = None
                else:
                    # stop playback
                    mx, my = event.pos
                    for r in range(PAD_ROWS):
                        for c in range(PAD_COLS):
                            pad_id = r * PAD_COLS + c
                            x = PADDING + c * (PAD_W + PADDING)
                            y = PADDING + r * (PAD_H + PADDING)
                            rect = pygame.Rect(x, y, PAD_W, PAD_H)
                            if rect.collidepoint(mx, my) and is_playing.get(pad_id):
                                dpads[pad_id].stop()
                                is_playing[pad_id] = False
                                break

        # Keyboard events
        elif event.type == pygame.KEYDOWN:
            key = pygame.key.name(event.key)
            if key.isdigit():
                pad_id = int(key) - 1
                if 0 <= pad_id < PAD_ROWS * PAD_COLS and dpads.get(pad_id):
                    dpads[pad_id].play(loops=-1)
                    is_playing[pad_id] = True
        elif event.type == pygame.KEYUP:
            key = pygame.key.name(event.key)
            if key.isdigit():
                pad_id = int(key) - 1
                if is_playing.get(pad_id):
                    dpads[pad_id].stop()
                    is_playing[pad_id] = False

    # Draw UI
    screen.fill((30, 30, 30))
    for r in range(PAD_ROWS):
        for c in range(PAD_COLS):
            pad_id = r * PAD_COLS + c
            x = PADDING + c * (PAD_W + PADDING)
            y = PADDING + r * (PAD_H + PADDING)
            rect = pygame.Rect(x, y, PAD_W, PAD_H)
            if recording_pad == pad_id:
                color = (200, 50, 50)
            elif is_playing.get(pad_id):
                color = (50, 200, 50)
            elif dpads.get(pad_id):
                color = (100, 100, 200)
            else:
                color = (80, 80, 80)
            pygame.draw.rect(screen, color, rect)
            pygame.draw.rect(screen, (0, 0, 0), rect, 2)
            label = font.render(str(pad_id+1), True, (255, 255, 255))
            screen.blit(label, label.get_rect(center=rect.center))

    pygame.display.flip()

# Cleanup
stream.stop()
stream.close()
pygame.quit()
