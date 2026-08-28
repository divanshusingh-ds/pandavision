# 🐼 PandaVision — Touchless Runner

> An original endless-runner game controlled through real-time computer vision and webcam-based motion tracking.

PandaVision is a computer-vision-powered endless runner built with Python and Pygame.  
Instead of relying completely on traditional keyboard controls, PandaVision uses a webcam to detect player movements and translate them into in-game actions.

The goal is simple:

**Move yourself → Control the Panda. 🐼**

---

## 🎮 Project Preview

PandaVision combines classic endless-runner gameplay with real-time webcam interaction.

### Core Concept

```text
              📷 Webcam
                  ↓
             OpenCV
                  ↓
          Motion Detection
                  ↓
          Gesture / Movement
              Detection
                  ↓
          Game Controller
                  ↓
             🐼 PANDA
