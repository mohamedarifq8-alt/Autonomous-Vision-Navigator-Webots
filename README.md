# Autonomous-Vision-Navigator-Webots
"Excited to share my latest engineering project! I developed an autonomous maze-solving system for the e-puck robot using Webots. By fusing high-level computer vision (OpenCV) for target tracking with low-level IR sensor data, the robot dynamically navigates obstacles using a right-wall following algorithm until it successfully locates its target. 
(# Webots e-puck: Autonomous Maze Solver & Target Tracker

![Python](https://img.shields.io/badge/Python-3.14+-blue.svg)
![Webots](https://img.shields.io/badge/Webots-R2025a-red.svg)
![OpenCV](https://img.shields.io/badge/OpenCV-4.x-green.svg)

## 📌 Project Overview
This project demonstrates the integration of **Computer Vision (High-level AI)** with **Hardware Sensor Control (Low-level Actuation)** using the e-puck robot within the Webots simulation environment. 

The robot is engineered to autonomously navigate a complex maze using a robust wall-following algorithm while simultaneously running a real-time object detection pipeline to locate a specific target (a red ball). Once the target is detected, the robot smoothly overrides its navigation protocol to approach and stop at the target.

## 🎥 Demonstration
*(Drop your GIF or Video link here showcasing the robot solving the maze and finding the ball)*

## 🧠 Core Engineering Features

* **Sensor Fusion:** Combines data from 8 IR distance sensors for obstacle avoidance and a simulated camera for environmental perception.
* **Right-Wall Following Algorithm:** Implements a reliable maze-solving strategy to escape local minimums and ensure complete environmental scanning.
* **Computer Vision Pipeline (OpenCV):**
    * **HSV Color Filtering:** Robust color detection that mitigates lighting variance.
    * **Morphological Transformations:** Utilizes mathematical morphology (Erosion and Dilation) to filter out floor reflections and visual noise.
    * **Centroid Tracking:** Calculates the object's moments to apply Proportional (P-control) steering towards the target.
* **Safety Clamping:** Hardware limits are hardcoded to ensure motor velocities never exceed physical specifications (`MAX_SPEED = 6.28`).

## 🛠️ Technology Stack
* **Environment:** Webots R2025a
* **Language:** Python
* **Libraries:** `controller` (Webots API), `cv2` (OpenCV), `numpy`

## 🚀 Installation & Usage

### 1. Prerequisites
Ensure you have Python installed and added to your system `PATH`. Install the required computer vision libraries:
```bash
pip install opencv-python numpy

### 2. Webots Setup
Clone this repository to your local machine.

Open the Webots simulator.

Load the world file located in worlds/your_maze_file.wbt.

Ensure the Webots Python command is correctly set:

Go to Tools -> Preferences -> Python command.

Set it to python.

3. Execution
Open the controller script controllers/ball_seeker/ball_seeker.py in the Webots text editor.

Click Build (if necessary), then click Reset and Play.

Two debug windows will appear displaying the raw camera feed and the binary AI mask, allowing real-time monitoring of the robot's visual processing.

👨‍💻 Author
Mohamed Arif Mahyoub Haider.
Electrical Engineer-Computer and Industrial Control.

This project was built to demonstrate the practical application of bridging software algorithms with physical (simulated) hardware components.)
