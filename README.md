# 🔐 Operation Locker Loot

A 3D top-down heist game built with Python and OpenGL. Navigate a bank vault, dodge laser beams, avoid vanishing trap tiles, and collect treasures before the 5-minute timer runs out!

---

## 🎮 Gameplay

You play as a thief infiltrating a bank. Move through a 12×12 grid, collect **15 treasures** scattered across the floor, and unlock the **Locker** for bonus points — all while evading:

- **Blinking lasers** that fire across the room every 2 seconds
- **Trap tiles** that vanish and reappear, dropping you if you fall through
- **Moving walls** that slide back and forth across your path
- A **5-minute time limit** — run out of time and it's game over

You start with **3 lives**. Hitting a laser or falling through a vanished tile costs one life.

---

## 🚀 Getting Started

### Prerequisites

- Python 3.x
- PyOpenGL

### Install dependencies

```bash
pip install PyOpenGL PyOpenGL_accelerate
```

> **Linux users** may also need GLUT:
> ```bash
> sudo apt-get install freeglut3-dev
> ```

### Run the game

```bash
python full_project.py
```

---

## 🕹️ Controls

### Movement

| Key | Action |
|-----|--------|
| `W` | Move forward |
| `S` | Move backward |
| `A` | Rotate left |
| `D` | Rotate right |

### Camera

| Key | Action |
|-----|--------|
| `C` | Toggle follow / fixed camera |
| `+` / `=` | Zoom in |
| `-` | Zoom out |
| `Q` | Rotate camera left |
| `E` | Rotate camera right |
| `Z` | Tilt camera down |
| `X` | Tilt camera up |

### Game Controls

| Key | Action |
|-----|--------|
| `R` | Restart game |
| `P` | Pause / Unpause |
| `M` | Toggle slow mode |

### Cheats

| Key | Cheat |
|-----|-------|
| `L` | Disable lasers for 10 seconds |
| `V` | Turn invisible for 5 seconds (immune to lasers) |
| `T` | Freeze trap tiles |

---

## 🏆 Scoring

| Event | Points |
|-------|--------|
| Small treasure | +points |
| Big treasure (30% chance) | +more points |
| Locker (unlocked after all treasures) | +100 points |

Collect all 15 treasures to reveal the **Locker** and complete the mission!

---

## 🗺️ Game Elements

- **Gray tiles** — safe floor
- **Red tiles** — trap tile about to vanish (warning!)
- **Missing tiles** — fallen trap, instant death if stepped on
- **Yellow coins** — small treasures
- **Gold chests** — big treasures
- **Green box** — the Locker (appears after all treasures are collected)
- **Red laser lines** — deadly when active, safe when off

---

## 📋 Requirements

```
Python >= 3.7
PyOpenGL
PyOpenGL_accelerate (optional, for better performance)
```
