# Overview
This project documents the development of Romi, a line-following, magnetometer tracking, and impact detecting autonomous robot. The goal is to complete a checkpoint based time trial, designed to demonstrate speed and reliability. 

# System Structure

## Hardware
 - Romi Chassis with 2 DC motors and quadrature encoders on a Power Distribution Board
 - Medium Density, 8 pin, line sensor array for line detection
 - BNO055 IMU for magnetometer, accelerometer, and gyroscope
 - Bump sensors, left and right
 - HC-05 for Bluetooth communication
 - Microcontroller: Nucleo STM32L467RG with Shoe of Brian

## Software
 - Real-Time Task Scheduling using (`cotask.py`)
 - FSM-Based Navigation managed by (`Thinker.py`)
 - PID Controller for closed loop control (`PIDController.py`)
 - Motor Control System (`Task_MotorController.py`)
 - Pre-programmed Path Execution (`PreProgPath.py`)
 - IMU and Sensor Fusion (`BNO055_Task.py`)
 - User Interface with a button for start/stop (`UI.py`)

# Modules

## **Motor and Encoder Control**
- `Driver_Motors.py`: Handles PWM-based motor control.
- `EncoderDriver.py`: Reads encoder counts to determine distance and velocity.
- `Task_MotorController.py`: Implements FSM for motor commands.

## **Sensor Integration**
- `LinesensorDriver.py` and `Task_LineFollower.py`: Detects and tracks line.
- `Driver_BumpSensor.py` and `Task_BumpSensor.py`: Detects physical obstacles.
- `BNO055_Driver.py` and `BNO055_Task.py`: IMU-based heading control.

## **Task Management**
- `cotask.py`: Implements a cooperative multitasking system.
- `task_share.py`: Manages shared variables between tasks.

## **Control Algorithms**
- **Line Following**: Uses PID control to adjust motor speed based on sensor input.
- **Heading Control**: IMU data is used to correct drift and maintain heading.
- **Bump Handling**: If a collision is detected, the robot stops and reorients.

## **Finite State Machine (FSM) Design**
- **STANDBY:** Wait for user input.
- **LINE_FOLLOW:** Follow the track using sensor data.
- **TURN_TO_HEADING:** Adjust based on IMU heading.
- **DRIVE_TO_HEADING:** Move in a set direction.
- **BUMP_RECOVERY:** Reverse and reorient if collision detected.
- **PREPROGRAMMED_PATH:** Execute a predefined movement sequence.

## **Challenges & Lessons Learned**
- **Sensor Calibration:** Required tuning of ADC readings for line detection.
- **IMU Noise:** Implemented filtering to stabilize heading readings.
- **Task Timing:** Optimized scheduling to ensure real-time response.

## **Video Demonstration**
[📹 Click Here to Watch the Robot in Action](#) *(Replace with actual video link)*

## **How to Run the Project**
1. Clone this repository:  
   ```bash
   git clone https://github.com/LucaSlade/Romulus.git
   ```
2. Flash the `main.py` script onto the Nucleo board.
3. Connect the sensors and motors as per `wiring` definitions.
4. Run the script and press the **Blue Button** to start.

### **Dependencies**
- **MicroPython** installed on STM32.
- **GitHub Pages / ReadTheDocs** for documentation.

## **Project Repository Structure**
```
/
├── EncoderDriver.py
├── Task_BumpSensor.py
├── PIDController.py
├── Driver_Motors.py
├── Task_MotorController.py
├── BNO055_Driver.py
├── LinesensorDriver.py
├── Task_LineFollower.py
├── UI.py
├── PreProgPath.py
├── cotask.py
├── Thinker.py
├── task_share.py
├── BNO055_Task.py
├── cqueue.py
├── shared.py
├── boot.py
├── main.py
└── README.md
```
- GitHub Repository URL: **[Link Here](#)**

---
**Developers:** Luca Sladavic & Aiden Theocheung 
*ME405 - Winter 2025*

