# Overview
This project documents the development of Romi, a line-following, magnetometer tracking, and impact detecting autonomous robot. The goal is to complete a checkpoint based time trial, designed to demonstrate speed and reliability. 

# System Components
The selected components listed below are the exact parts used to build Romulus.

## Hardware

### Bare Chassis
 - Polulu Romi Chassis (https://www.pololu.com/product/3543) with 2 DC motors and quadrature encoders on a Power Distribution Board (https://www.pololu.com/category/202/romi-chassis-and-accessories)
   
   ![image](https://github.com/user-attachments/assets/b956889f-ea22-409b-a902-341a7f98214e)
   
   ![image](https://github.com/user-attachments/assets/d46982f6-1200-4fad-9ba3-adbe45e9ad82)
   
   ![image](https://github.com/user-attachments/assets/4d4acbbf-08e0-495b-ae4f-8ddb10b1f286)
   
### Reflectance Sensors
 - Medium Density, 8 pin, line sensor array for line detection. Placed at the front of Romi to ensure consistency
(https://www.pololu.com/product/4248)
   
   ![image](https://github.com/user-attachments/assets/4e1546af-2b07-4769-b3ee-b79c8f58e74d)

### IMU Sensor
 - BNO055 IMU for magnetometer, accelerometer, and gyroscope

    ![image](https://github.com/user-attachments/assets/f62a0d6f-61af-412b-a289-89edeebfb996)

### Bump Sensor
 - Bump sensors, left and right in arrays of 3 (https://www.pololu.com/product/3674)
   
   ![IMG_1572](https://github.com/user-attachments/assets/b209eb08-c4de-4f03-b35a-a715138de331)

### Bluetooth
 - HC-05 for Bluetooth communication

   ![image](https://github.com/user-attachments/assets/68cd8d92-45d1-43fa-b19d-d5c2a4f3f1bb)

### Microcontroller
 - Nucleo STM32L467RG using Micropython in conjunction with Shoe of Brian to provide ntaive USB port for use with Micropython code.
   
   ![IMG_1574](https://github.com/user-attachments/assets/9b4dd78d-4063-4082-88b0-de0faad976a4)



## Wiring

### Nucleo-L476RG Pin-Out
![image](https://github.com/user-attachments/assets/c99ff21e-69ee-4c86-9c41-ca0374ef0554)

### Motor and Encoder Pins
![image](https://github.com/user-attachments/assets/bf40cc08-10dc-46d4-9f17-839ccc3add1d)

### Reflectance Sensor Pins
![image](https://github.com/user-attachments/assets/9dcbb88e-57d0-45c5-9984-47b6caa1b1a4)

### IMU Sensor Pins
![image](https://github.com/user-attachments/assets/e819c08f-241a-4fe8-9d49-252e000e962b)

### Bump Sensor Pins
![image](https://github.com/user-attachments/assets/da58d381-31b4-48a6-8f8b-5fbec43da63b)

### Bluetooth Pins
![image](https://github.com/user-attachments/assets/f47b0679-5dfb-4168-9fd3-4f8072a4b637)

### Voltage Divider Pins
![image](https://github.com/user-attachments/assets/2343a4bd-07c2-4d5c-b4ba-65d58d46c4fc)


## Software

# Modular Structure
Each piece listed above is individually implemented into a navigation task allowing for various combinations of obstacles to be overcome with ease along a specified course. This structure is essential for adaptability and larger tracks.

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
 - **Heading Control**: IMU data is used to correct drift and maintain heading while spinning in place.
 - **Stright Drive**: Incorporates PID control to maintain a given direction and adjust accordingly while driving.

## **FSM Navigation Design**

<img width="1199" alt="PNG image" src="https://github.com/user-attachments/assets/ce47362c-863d-499f-821f-1660cbe8d39f" />


- **S0_STANDBY:** Wait for user input. In this state we are waiting for the started flag and then transferring into line follow. 
 - **S1_LINE_FOLLOW:** Follow the track using sensor data. Line follow until the diamond is reached. This is about 5000 encoder ticks. The encoder will update and count up with the driver until this number is reached. 
 - **S2_STRAIGHT_DRIVE:** Move in a set direction. Then move for a set amount of encoder ticks until the diamond is passed. 
 - **S3_LINE_FOLLOW:** Follow the track using sensor data. Through the curve, the dotted section, the larger curve, and through the lines. 
- **S4_STRAIGHT_DRIVE:** Drive straight through the cage until a position 26 inches from the starting dot is reached. This will ensure that after turning the robot will be able to exit the gate.  
 - **S4_TURN_TO_HEADING:** Turn to a set direction. Turn to a position 270 degrees from the starting position and aligned with the gates.  
 - **S5_STRAIGHT_DRIVE:** Move straight for a small amount of encoder ticks to allow the line sensor to find the line. 
 - **S7_LINE_FOLLOW:** Follow the track using sensor data toward the wall. 
 - **S8_REVERSE:** Reverse away from wall after collision for an amount of encoder ticks where the cup is perfectly perpendicular from the center of Romi. 
 - **S9_TURN_TO_HEADING:** Turn to the same heading as set in the initial starting state. 
 - **S10_DRIVE_TO_FINISH:** Use the IMU and encoder distance to make 3 straight segments and two turns before stopping which will be hard coded in.
   
![image](https://github.com/user-attachments/assets/493b43d8-09ba-46a5-ab61-3681c30bc686)


### Course
![IMG_1577](https://github.com/user-attachments/assets/ec4ebac2-cb3e-47ae-a8a1-ab696d0dd84d)

- The image below contains the information of the states that we hoped to follow. 
![IMG_35240B1DF5D7-1](https://github.com/user-attachments/assets/fad4090d-a99d-4e4f-ba21-e95bcbf206b2)

# Reference Diagrams

## Task Diagram
<img width="811" alt="Task_Diagram" src="https://github.com/user-attachments/assets/8115b79a-1323-4171-b656-9068fde3d2c9" />

## Thinker FSM
<img width="1214" alt="Screenshot 2025-03-16 at 10 28 48 PM" src="https://github.com/user-attachments/assets/9d4ce456-eced-40c8-b4fb-1bec9b4714c5" />

## Line Follower FSM
<img width="522" alt="Screenshot 2025-03-16 at 10 29 05 PM" src="https://github.com/user-attachments/assets/7d9ad0bc-4038-449d-bea9-f31b16e1efad" />

## BNO055 FSM
<img width="594" alt="Screenshot 2025-03-16 at 10 29 15 PM" src="https://github.com/user-attachments/assets/fe8ef6e2-0174-4da8-b37d-abd7eed438c3" />

## Bump Sensor FSM
<img width="493" alt="Screenshot 2025-03-16 at 10 29 22 PM" src="https://github.com/user-attachments/assets/dbbba814-2c71-4e80-88df-b18e766a13f9" />

## Motor Controller FSM
<img width="422" alt="Screenshot 2025-03-16 at 10 29 28 PM" src="https://github.com/user-attachments/assets/7203cbb0-4e1d-4429-857e-f85da27acb27" />

## Overall Code Structure
- At the top we have our high level code which we use to create objects, tasks, and run the scheduler. Between is the Middle Level code which implements each generator function and uses the share information. At the low level is the code that interfaces with the hardware. This is where each driver is created.

# Results

Each individual task in this project was developed and tested independently to ensure proper functionality. The line-following, bump detection, IMU-based heading control, pre-programmed path execution, and motor control tasks all performed reliably in isolation. However, integrating them into a single cohesive system proved to be one of the most significant challenges of the project.

One of the major difficulties was ensuring smooth state transitions within the finite state machine. While each task worked well individually, unpredictable interactions between them—such as delays in sensor readings, conflicts between line-following and pre-programmed movement, or inconsistent timing of bump sensor detections—often led to erratic robot behavior. Fine-tuning task priorities and execution timing was crucial to achieving a functional system.

The PID controllers played a critical role in motor speed regulation and heading adjustments. Proportional Gain was the most reliable and effective, providing a steady and predictable correction. Integral Gain was highly sensitive and required very careful tuning. Even small changes often caused excessive oscillations or unintended drift. Derivative Gain was also challenging to tune, as it amplified noise from the sensors, making the system unstable in certain conditions. Ultimately, a P-dominant control strategy was found to be the best approach, with minimal contributions from I and D to prevent excessive corrections and instability.

One of the most impactful discoveries was the significant impact of battery charge on performance and reliability. When the battery voltage was high, the robot moved faster and responded more predictably. However, as the charge decreased, the motors became sluggish, sensor readings varied more, and timing inconsistencies emerged—especially in tasks relying on precise movements, such as line-following and heading corrections. The varying power levels also altered the effectiveness of the PID controllers, requiring more frequent recalibrations than expected.

Moving forward, a battery voltage monitoring system would be a valuable addition to automatically adjust motor effort and PID parameters based on available power.

# **Challenges & Shortcomings**
 - Implementing Bluetooth: Since there was no common structure for how to incorporate Bluetooth communication, finding the path to successful wireless instruction took many hours of trial and error to find the right baudrate and UART channel. Even after proper configuration and setup, the module would only receive and write once every 20-30 minutes. Looking back avoiding Bluetooth overall would save much more time than the value that it provided.
 - IMU noise: The controller for the heading changes would often over saturate and rotate farther than desired. A solution was to implement filtering to stabilize readings, allowing the heading to have a small range instead of a single fixed value.
 - Task Timing: A rather large challenge was tuning the task period and priorities to ensure reliability and speed. If more time was permitted, this design would have had much more time efficient task periods to avoid tasks running late consistently.
 - Implementing Voltage Divider: Although a working voltage divider was built using 3 wires, a 15.2 kOhm, and a 7 kOhm resistor, there was not enough time to write the code to read the voltage readings directly from the batteries and incorporate this into a motor effort. This bypass allows for higher power efficiency allowing the rechargeable batteries to be used for longer periods of time without a recharge.
 - Coordinate Tracking: If more time was permitted, a coordinate system to keep track of the location of Romulus in 2D space would aid in completing the course in the fewest amount of orientation and straight path changes as possible. This would have been implemented with encoder and heading tracking.



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
- **MicroPython** installed on Nucleo board.
- **GitHub Pages / ReadTheDocs** for documentation.

```
- GitHub Repository URL:
  
  (https://github.com/LucaSlade/ME405-Romulus.git)

---
**Developers:** Luca Sladavic & Aiden Theocheung 

*ME405 - Winter 2025*

