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
🖐️ Touchless Gameplay

The planned control system allows real-world movements to trigger actions inside the game.

For example:

🙋 Player Movement
       ↓
📷 Webcam
       ↓
🧠 Computer Vision
       ↓
⚡ Movement Detected
       ↓
🐼 Panda Action

Possible actions include:

Player Movement	Game Action
Move left	Move left
Move right	Move right
Jump movement	Jump
Duck movement	Duck
Hand wave	Start / interaction

The exact gesture mapping continues to evolve during development.

🌿 PandaVision World

The game is being designed around an original Panda-themed environment.

Planned game elements include:

🎋 Bamboo
🪨 Rocks
🪵 Logs
🌳 Trees
🐦 Flying obstacles
☁️ Clouds
☀️ Day environment
🌙 Night environment

The goal is to create a recognizable world rather than simply recreating an existing runner game.

🏆 Scoring System

PandaVision includes a score-based endless-runner system.

The game tracks:

SCORE
BEST SCORE
COINS

As the player survives longer, the game becomes progressively more challenging.

Difficulty progression
Start
  ↓
Normal Speed
  ↓
More Obstacles
  ↓
Higher Speed
  ↓
Faster Reactions
  ↓
More Difficult Gameplay
🧠 Technology Stack
Technology	Purpose
🐍 Python	Main programming language
🎮 Pygame	Game development and rendering
📷 OpenCV	Webcam processing and computer vision
🖐️ MediaPipe	Landmark / gesture detection
🎨 Pixel Art	Game visual style
🛠️ Core Technical Concepts

PandaVision is also a learning project covering several important programming and computer-science concepts.

Game Development
Game loops
Event handling
Player physics
Gravity
Jump mechanics
Collision detection
Object movement
Animation
Score systems
Difficulty scaling
Computer Vision
Webcam input
Real-time frame processing
Motion tracking
Landmark detection
Gesture recognition
Coordinate mapping
Real-Time Systems

The game continuously processes:

Camera Input
     +
Computer Vision
     +
Game Physics
     +
Rendering
     +
User Interaction

all within a real-time game loop.

📁 Project Structure
PandaVision/
│
├── main.py
│
├── assets/
│   ├── panda/
│   │   ├── panda_run1.png
│   │   ├── panda_run2.png
│   │   ├── panda_jump.png
│   │   └── panda_gameover.png
│   │
│   ├── environment/
│   ├── obstacles/
│   └── sounds/
│
├── computer_vision/
│   ├── motion_tracking.py
│   └── gesture_detection.py
│
├── README.md
└── requirements.txt

The project structure may change as development continues.

🚀 Getting Started
1. Clone the Repository
git clone https://github.com/YOUR-USERNAME/PandaVision.git

Enter the project directory:

cd PandaVision
2. Install Dependencies

Install the required Python packages:

pip install pygame opencv-python mediapipe

If a requirements.txt file is available:

pip install -r requirements.txt
3. Run PandaVision
python main.py

Make sure your webcam is connected and available if you are using webcam-based controls.

🎮 Development Controls

During development, keyboard controls can be used for testing.

Key	Action
SPACE	Jump
↑	Jump
←	Move Left
→	Move Right
↓	Duck
ESC	Exit

The long-term goal is to minimize or remove the need for keyboard controls.

📸 Webcam Mode

When webcam mode is enabled, PandaVision displays the camera feed and processes player movement.

The game can provide information such as:

OPENCV MOTION TRACKING

GAME RUNNING

ACTION: JUMP

LANE: CENTER

This makes the computer-vision system visible during development and demonstration.

🏗️ Development Roadmap

PandaVision is an evolving project.

✅ Current
 Basic endless-runner gameplay
 Pygame game loop
 Panda-themed game concept
 Player physics
 Jump mechanics
 Obstacle system
 Collision detection
 Score system
 Increasing difficulty
 Webcam integration
 OpenCV motion tracking
 Real-time game status display
🔨 In Development
 Smooth Panda running animation
 Improved Panda character system
 Multiple obstacle types
 Better collision hitboxes
 Advanced gesture recognition
 Smooth lane movement
 Improved webcam tracking
 Sound effects
 Background music
 Day/night cycle
 Improved environment
 Game start screen
 Pause system
 Game-over screen
 Restart system
🚀 Future
 Fully keyboard-free gameplay
 Advanced hand-landmark controls
 More Panda animations
 More environments
 Special abilities
 Power-ups
 Persistent high scores
 Performance optimization
 Improved visual effects
 Complete polished release
💡 Project Vision

PandaVision started as a simple runner-game experiment.

The idea gradually evolved into something bigger:

Create a game that can understand the player.

Instead of pressing a button to tell the game what to do, the player can use physical movement to interact with the game.

The long-term vision is to explore how computer vision can make gaming more natural, accessible and interactive.

🔬 What I Learned From This Project

Building PandaVision involves learning and applying:

Python programming
Pygame development
Game physics
Collision detection
Object-oriented game design
Real-time rendering
Webcam processing
OpenCV
MediaPipe
Motion tracking
Gesture recognition
Coordinate systems
Animation systems
Real-time input processing
Debugging and optimization

This project is not only about making a game.

It is about understanding how different technologies can work together to create an interactive system.

🎥 Demo
PandaVision in action

Add your demo video or GIF here.

Example:

📷 Webcam ON
       ↓
🙋 Player moves
       ↓
🧠 Computer Vision detects movement
       ↓
⚡ Action generated
       ↓
🐼 Panda responds
       ↓
🎮 Game continues
🌟 Why I Built PandaVision

I wanted to experiment with the combination of game development and computer vision.

Instead of building another ordinary game controlled only by a keyboard, I wanted to explore:

Can a webcam become a game controller?

PandaVision is my attempt to answer that question.

🐼 The Goal

The final experience should feel like this:

        YOU
         │
         │  Move
         ▼
     📷 WEBCAM
         │
         ▼
   🧠 COMPUTER VISION
         │
         ▼
      🎮 GAME
         │
         ▼
       🐼 PANDA
No traditional controller required.
Just movement.
Just interaction.
Just PandaVision. 🐼
📌 Project Status

🚧 Active Development

PandaVision is continuously being improved with new gameplay mechanics, computer-vision features, animations and visual elements.

The current version is a working prototype, while the ultimate goal is a polished touchless endless-runner experience.

👨‍💻 Developer

Deepu

Built with:

Python + Pygame + OpenCV + Computer Vision

⭐ Support

If you find the project interesting:

⭐ Star the repository
🍴 Fork the project
💡 Share feedback
🚀 Follow the development

📜 License

This project is created for educational, experimental and portfolio purposes.

The project uses original PandaVision concepts and assets developed for this project.

<p align="center">
🐼 PandaVision
Move Yourself. Control the Panda.

Built with Python • Pygame • OpenCV • Computer Vision

</p> ```
