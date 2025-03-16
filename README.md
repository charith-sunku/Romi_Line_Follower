#  Romi Line-Following Robot
**By Charith Sunku and Tomas Franco**

## Table of Contents
1. [Project Objective](#project-objective)
2. [Hardware Elements](#hardware-elements)
3. [Electro-Mechanical Design](#electro-mechanical-design-overview)
4. [Firmware Design](#firmware-design-overview)
5. [Task Breakdown](#task-breakdown)
   1. [Tasks and Shares](#tasks-and-shares)
   2. [Finite State Machine Diagrams](#finite-state-machine-diagrams)
   3. [User Interaction Task](#user-interaction-task)
   4. [Actuation Task](#actuation-task)
   5. [IR Task](#ir-task)
   6. [Controller Task](#controller-task)
   7. [Dead Reckoning Task](#dead-reckoning-task)

## Project Objective
The objective of the Romi robot is to navigate the game track, hitting each checkpoint in sequence. Before returning to chekpoint 6, the robot must interact with the wall in some capacity to acknowledge the wall's presence. Our solution was to use a IR reflectance sensor to perform line following and a 9-DOF IMU to navigate through sections without trackable lines. 

![Annotated Game Track](https://github.com/user-attachments/assets/ff8461aa-9a42-4708-82e6-f4fdfe3421d9)

[Romi Demo Video](https://youtu.be/yved8C4mFfU)

---
## Hardware Elements
1. Polulu Romi Chassis Kit
2. Polulu Motor Driver and Power Distribution Board for Romi Chassis
3. Polulu Romi Pair Encoder Kit
4. NUCELO-L476RG Development Board
5. Shoe of Brian Carrier Baseboard (adds Micropython capability)
6. Polulu QTR-HD-13A Reflectance Sensor Array (IR Sensor)
7. Adafruit BNO055 Breakout Board (IMU Sensor)

## Electro-Mechanical Design Overview:
1. **Hardware Mounting**: All sensors and control boards were mounted on laser-cut acrylic plates, using standoffs to secure each component at the correct height and orientation. This custom acrylic approach provided a sturdy yet lightweight frame to house the IR sensor array, IMU, and bump sensors in stable positions around the chassis. By carefully aligning the cut-outs, wiring was neatly routed, reducing potential interference or accidental disconnections. The modular nature of acrylic plates and standoffs also simplifies maintenance and future upgrades, as sensors can be repositioned or swapped without heavily modifying the robot’s overall structure.
   
2. **Electrical Wiring**: Power is supplied via a 6 × AA battery pack feeding a dedicated power distribution board. The motor drivers, NUCLEO microcontroller, and encoders all draw regulated voltage from this board, ensuring they receive stable, isolated power rails. This design isolates higher-current paths for the motors while providing a clean supply for sensitive components like sensors and the microcontroller, minimizing electrical noise and enhancing overall reliability. Below is a detailed wiring diagram highlighting the digital connections between the microcontroller and sensor peripherals.

![Romi Wiring Diagram](https://github.com/user-attachments/assets/9cdc2165-dc94-408c-babd-3128b9f02dd3)

## Firmware Design Overview
1. **Hardware Drivers**: Each hardware component—motors, sensors, encoders, and the IMU—is managed by a dedicated driver that encapsulates the microcontroller’s low-level specifics (pin assignments, registers, timers, etc.). By providing clear, high-level methods, these drivers hide the intricate setup details from the rest of the codebase. This approach keeps the system modular and maintainable: if hardware pins or peripherals change, only the corresponding driver needs updating, while the rest of the application remains unaffected. It also streamlines debugging and testing, because each component’s functionality can be verified in isolation without juggling microcontroller minutiae in every part of the project.
   
2. **Line Following**: The robot features an array of IR sensors arranged to detect the difference in reflectivity between the line and surrounding surface. By sampling each sensor’s value, the code computes a “centroid” of reflectance, effectively determining the line’s relative position. A simple PI controller (proportional, integral terms) then adjusts motor speeds to steer the robot back toward the line’s center. This setup allows the robot to smoothly track curves and handle minor deviations, ensuring continuous, stable line following across varying course layouts.
   
3. **Heading Control**: A BNO055 IMU provides real-time heading data (Euler angles), enabling more advanced maneuvers beyond standard line following. The robot’s code compares this heading to a desired reference angle, and a controller applies proportional corrections to the motor outputs. This approach lets the robot rotate to precise angles—such as 90° for “diamond mode” or 180° for reversing—without relying solely on line-sensing. By decoupling orientation from visual tracks, the system remains robust even when the line is missing or deliberately ignored (e.g., during dead-reckoning segments).
   
4. **Cooperative Multitasking**: The system is organized into distinct tasks—such as IR sensor readings, motor control, and user interaction—each running in a cooperative scheduler (via cotask.py and task_share.py). Rather than use a traditional preemptive RTOS, this approach allows each task to execute sequentially, yielding control back to the scheduler when finished. As a result, the robot remains responsive while the codebase stays modular, making it easier to debug individual tasks and manage shared data without complex thread-synchronization overhead.

## Task Breakdown
To facilitate cooperative multitasking, the different hardware/software operations of Romi were split into different tasks. Each task in charge of operating a different aspect of the system. Our design has 6 tasks:
1. User Interaction
2. Actuation
3. IR
4. Controller
5. Dead Reckoning

### Tasks and Shares
Each task runs at a different period and each task is assigned a priority. Some tasks such as Actuation and IR must be run at higher frequencies as their hardaware needs to be manipulated more often. Tasks that are run more frequently are given a lower priority. This allows tasks that run at a lower frequency to take priority in case two tasks with different priorities are called simultaneously. Tasks are created by defining Python generator functions that represent each task. These functions are then used with the `cotask.py` module to create tasks with defined periods and priorities. The transfer of all inter-task variables is done with the `task_share.py`. This module creates `Share` objects that are passed into each task. Each task also has the ability to read and write to the Shares it has access to. Below is a task diagram showing the periods and priorities of each task. Additionally, the transfer of information through inter-task variables is also shown. 

***INSERT TASK DIAGRAM HERE***

### Finite State Machine Diagrams
Each task consists of several states that further subdivide the tasks into smaller operations. As each task is run, its current state is executed and updated based on the state of inter-task variables. This allows each task to execute operations efficiently and cede to other tasks as needed, allowing for cooperative multitasking. 

### User Interaction Task
### Actuation Task
### IR Task
### Controller Task
### Dead Reckoning Task
---

