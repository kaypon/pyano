# Pygame One-Octave Piano with Recording

A simple Python application that displays a one-octave piano keyboard using Pygame and NumPy, allows you to play notes via mouse clicks or keyboard shortcuts, and record your performance to a WAV file.

## Features

- **One octave** (C4–B4) with corresponding black keys.
- **Keyboard shortcuts**: Z/S/X/D/C/V/G/B/H/N/J/M for white/black keys.
- **Mouse & keyboard support**: Click or hold keys to play; supports polyphony and sustained notes.
- **Key highlighting** while pressed.
- **Record/Stop** button to capture exactly what you play, exported as a normalized WAV.

## Dependencies

- Python 3.7+
- [Pygame](https://www.pygame.org/) (audio & GUI)
- [NumPy](https://numpy.org/) (signal generation)

Install via pip in a virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install pygame numpy
```

## Files

- `piano.py`: Main application script.

## Usage

Run the script from your activated virtual environment:

```bash
python piano.py
```

### Controls

- **Mouse**: Click and hold white or black keys to play notes.
- **Keyboard**:
  - `Z` → C4
  - `S` → C♯4
  - `X` → D4
  - `D` → D♯4
  - `C` → E4
  - `V` → F4
  - `G` → F♯4
  - `B` → G4
  - `H` → G♯4
  - `N` → A4
  - `J` → A♯4
  - `M` → B4

Pressed keys will be highlighted on-screen.

## How It Works

1. **Audio Generation**: Builds 1-second sine-wave buffers for each MIDI pitch in the octave using NumPy.
2. **Playback**: Loops sound objects on key/mouse down, stops on release for sustained polyphony.
3. **Recording**: Logs timestamped press/release events, then reconstructs a composite waveform buffer and writes it to a WAV file.