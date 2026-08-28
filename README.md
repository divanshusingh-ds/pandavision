# 🐼 PandaVision — Touchless Runner

<p align="center">
  <img src="assets/panda_logo.png" alt="PandaVision Logo" width="180">
</p>

<h3 align="center">
  🐼 An Original Endless Runner Controlled with Computer Vision
</h3>

<p align="center">
  <b>Move yourself. Control the Panda.</b>
</p>

---

## 🎮 About PandaVision

**PandaVision** is an original endless-runner game built with **Python, Pygame, OpenCV and computer vision techniques**.

The project combines traditional game development with real-time webcam interaction to create a more natural and interactive gaming experience.

Instead of depending only on a keyboard, PandaVision is designed to understand the player's movement through a webcam and convert it into actions inside the game.

### The idea is simple:

**Camera → Computer Vision → Movement Detection → Game Action → 🐼 Panda**

PandaVision is being developed as an experiment in **touchless gaming and human-computer interaction**.

---

## ✨ What Makes PandaVision Different?

Traditional runner games usually depend on:

- Keyboard
- Mouse
- Touch controls
- Game controllers

PandaVision explores another approach:

> **What if your physical movement could become the game controller?**

The project combines:

**🎮 Game Development**  
**📷 Computer Vision**  
**🖐️ Gesture & Motion Detection**  
**🐍 Python Programming**  
**⚡ Real-Time Interaction**

into one project.

---

# 🐼 Game Features

## 🎮 Endless Runner Gameplay

PandaVision follows the classic endless-runner concept where the player must keep the Panda alive while avoiding obstacles.

Current gameplay includes:

- Endless running
- Jump mechanics
- Gravity and physics
- Obstacle movement
- Collision detection
- Score tracking
- Increasing difficulty
- Best-score tracking
- Coin counter
- Game status information

---

## 📷 Real-Time Webcam Tracking

One of the main features of PandaVision is webcam-based interaction.

The webcam captures the player's movement and the computer vision system processes the camera feed in real time.

### Processing pipeline

```text
           📷 WEBCAM
               │
               ▼
        ┌───────────────┐
        │    OpenCV     │
        │ Camera Input  │
        └───────┬───────┘
                │
                ▼
        Motion Detection
                │
                ▼
       Gesture / Movement
           Recognition
                │
                ▼
        Game Controller
                │
                ▼
             🐼 PANDA
