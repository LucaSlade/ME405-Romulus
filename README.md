# Overview
This project documents the development of Romi, a line-following, magnetometer tracking, and impact detecting autonomous robot. The goal is to complete a checkpoint based time trial, designed to demonstrate speed and reliability. 

# System Components
The selected components listed below are the exact parts used to bulid Romulus.

## Hardware

### Bare Chassis
 - Polulu Romi Chassis (https://www.pololu.com/product/3543) with 2 DC motors and quadrature encoders on a Power Distribution Board (https://www.pololu.com/category/202/romi-chassis-and-accessories)
   ![image](https://github.com/user-attachments/assets/b956889f-ea22-409b-a902-341a7f98214e)
   ![image](https://github.com/user-attachments/assets/d46982f6-1200-4fad-9ba3-adbe45e9ad82)
   ![image](https://github.com/user-attachments/assets/4d4acbbf-08e0-495b-ae4f-8ddb10b1f286)
   
### Reflectance Sensors
 - Medium Density, 8 pin, line sensor array for line detection. Placed at the front of Romi to 
   ![image](https://github.com/user-attachments/assets/4e1546af-2b07-4769-b3ee-b79c8f58e74d)

### IMU Sensor
 - BNO055 IMU for magnetometer, accelerometer, and gyroscope
   ![image](https://github.com/user-attachments/assets/f62a0d6f-61af-412b-a289-89edeebfb996)

### Bump Sensor
 - Bump sensors, left and right
   ![IMG_1572](https://github.com/user-attachments/assets/b209eb08-c4de-4f03-b35a-a715138de331)

### Bluetooth
 - HC-05 for Bluetooth communication
   ![image](https://github.com/user-attachments/assets/68cd8d92-45d1-43fa-b19d-d5c2a4f3f1bb)

### Microcontroller
 - Nucleo STM32L467RG using Micropython in conjunction with Shoe of Brian to provide ntaive USB port for use with Micropython code.
   ![IMG_1574](https://github.com/user-attachments/assets/9b4dd78d-4063-4082-88b0-de0faad976a4)


## Software

### Tasks

 - Real-Time Task Scheduling using (`cotask.py`)
 - FSM-Based Navigation managed by (`Thinker.py`)
 - PID Controller for closed loop control (`PIDController.py`)
 - Motor Control System (`Task_MotorController.py`)
 - Pre-programmed Path Execution (`PreProgPath.py`)
 - IMU and Sensor Fusion (`BNO055_Task.py`)
 - User Interface with a button for start/stop (`UI.py`)

# Modular Structure
Each piece listed above is individually implemented into a navigation task allowing for various combinations of obstacles to be overcame with ease along a specified course. This structure is essential for adaptability and larger tracks.

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

## **FSM Navigation Design**
 - **STANDBY:** Wait for user input.
 - **LINE_FOLLOW:** Follow the track using sensor data.
 - **TURN_TO_HEADING:** Adjust based on IMU heading.
 - **DRIVE_TO_HEADING:** Move in a set direction.
 - **BUMP_RECOVERY:** Reverse and reorient if collision detected.
 - **PREPROGRAMMED_PATH:** Execute a predefined movement sequence.

### Course
![IMG_1577](https://github.com/user-attachments/assets/ec4ebac2-cb3e-47ae-a8a1-ab696d0dd84d)


# **Challenges & Shortcomings**
 - Implementing Bluetooth: Since there was no common structure for how to incorporate Bluetooth communicaiton, finding the path to successful wireless instruction took many hours of trial and error to find the right baurate and UART channel.
 - **IMU Noise:** Implemented filtering to stabilize heading readings.
 - **Task Timing:** Optimized scheduling to ensure real-time response.
 - Implementing Voltage Divider: Did not have enough time to write the code to read the voltage readings directly from the batteries and incorporate this into a motor effort.


# Red Carpet
![IMG_1585](https://github.com/user-attachments/assets/eea66b2e-44d2-42e8-b5b0-49359c76650b)
![IMG_1581](https://github.com/user-attachments/assets/388108d3-37fd-46db-a0b2-8a54390434bc)


# **Video Demonstration**
[📹 Click Here to Watch the Robot in Action](https://www.youtube.com/watch?v=LcPKkkXOCas)



# **How to Run the Project**
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

# **Project Repository Structure**
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
- GitHub Repository URL: (https://github.com/LucaSlade/ME405-Romulus.git)

---
**Developers:** Luca Sladavic & Aiden Theocheung 
*ME405 - Winter 2025*

