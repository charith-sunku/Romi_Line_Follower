#  Romi Line-Following Robot
**By Charith Sunku and Tomas Franco**

## Table of Contents
1. [Project Objective](#project-objective)
2. [Hardware Elements](#hardware-elements)
3. [Electro-Mechanical Design](#electro-mechanical-design-overview)
4. [Firmware Design](#firmware-design-overview)
5. [Task Breakdown](#task-breakdown)
   1. [Tasks](#tasks)
   2. [Shares](#shares)
   3. [Finite State Machine Diagrams](#finite-state-machine-diagrams)
   4. [User Interaction Task](#user-interaction-task)
   5. [Actuation Task](#actuation-task)
   6. [IR Task](#ir-task)
   7. [Controller Task](#controller-task)
   8. [Dead Reckoning Task](#dead-reckoning-task)

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

![Romi Wiring Diagram](https://github.com/user-attachments/assets/e3bc8fe7-d673-4d7d-90d2-31c6a407f0b3)

3. **Motor Characterization**: The motors we used were characterized reading from encoder.py and running them at various PWM.
<img width="545" alt="Screenshot 2025-03-16 at 2 44 07 PM" src="https://github.com/user-attachments/assets/0b1ea5cd-85fc-4f90-8878-692afc1c8530" />
**Figure 1.** Step Response of Right Motor Position comparing PWM values ranging from 0-70% 

<img width="545" alt="Screenshot 2025-03-16 at 2 44 32 PM" src="https://github.com/user-attachments/assets/b819427d-9bf0-4717-9bfa-c96f700bb643" />
**Figure 2.** Step Response of Left Motor Position comparing PWM values ranging from 0-70% 

<img width="545" alt="Screenshot 2025-03-16 at 2 44 50 PM" src="https://github.com/user-attachments/assets/accba3bf-fdf2-4bb9-9973-dc39e970cf11" />
**Figure 3.** Step Response of Right Motor Velocity comparing PWM values ranging from 0-70% 

<img width="545" alt="Screenshot 2025-03-16 at 2 45 38 PM" src="https://github.com/user-attachments/assets/ce891e6a-a171-4bb1-bdba-bd71bd6a3354" />
**Figure 4.** Step Response of Left Motor Velocity comparing PWM values ranging from 0-70% 

<img width="492" alt="Screenshot 2025-03-16 at 2 46 10 PM" src="https://github.com/user-attachments/assets/7b4d431a-87fd-4c20-94b2-3d13cc7b84df" />
**Figure 5.** Steady-State Velocity of Right Motor at PWM Step Input Ranging from 0-70% showing Motor Gain and Startup Effort 

![image](https://github.com/user-attachments/assets/59066775-565a-4ad6-8435-9c45657f5200)
**Figure 6.** Steady-State Velocity of Left Motor at PWM Step Input Ranging from 0-70% showing Motor Gain and Startup Effort 

<img width="535" alt="Screenshot 2025-03-16 at 2 47 28 PM" src="https://github.com/user-attachments/assets/bead682e-726b-4d20-85d6-142150f10ccf" />
**Figure 7.** Linearized Step Responses for the Right Motor at Various PWM Efforts ranging from 10–70% Overlaid with a Global Best-Fit Line (τ ≈ 0.074 s) for the Motor Step Response Experiment. 

<img width="535" alt="Screenshot 2025-03-16 at 2 47 54 PM" src="https://github.com/user-attachments/assets/056e3095-c60b-40cf-94a2-c145ab76bcdb" />
**Figure 8.** Linearized Step Responses for the Left Motor at Various PWM Efforts ranging from 10–70% Overlaid with a Global Best-Fit Line (τ ≈ 0.077 s) for the Motor Step Response Experiment. 

 

 

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

### Tasks
Each task runs at a different period and each task is assigned a priority. Some tasks such as Actuation and IR must be run at higher frequencies as their hardaware needs to be manipulated more often. Tasks that are run more frequently are given a lower priority. This allows tasks that run at a lower frequency to take priority in case two tasks with different priorities are called simultaneously. Tasks are created by defining Python generator functions that represent each task. These functions are then used with the `cotask.py` module to create tasks with defined periods and priorities. Below is a task diagram showing the periods and priorities of each task. Additionally, the transfer of information through inter-task variables is also shown. 

***INSERT TASK DIAGRAM HERE***

### Shares
The transfer of all inter-task variables is done with the `task_share.py`. This module creates `Share` objects that are passed into each task. Each task also has the ability to read and write to the Shares it has access to. Using `Share` objects avoids the use of global variables as inter-task variables.

| **Share Name**      | **Data Type** | **Description**                     |
|---------------------|---------------|--------------------------------------|
| `system_done`       | Unsigned Char| When set, this flag tells all tasks to stop operation and end system. |
| `R_pwm_effort`      | Signed Float | PWM effort to be given to the right motor.|
| `L_pwm_effort`      | Signed Float | PWM effort to be given to the left motor.|
| `calibration`       | Signed Short | Flag controls the process of calibrating the IR sensor. When incremented to 3, calibration is complete.|
| `centroid`          | Signed Float | Centroid of the IR sensor that indicates position of black line relative to IR array.|
| `diamond`           | Signed Char  | Flag that controls start and end of diamond section of the track.|
| `romi_heading`      | Signed Float | Heading of Romi relative to initial heading on startup, expressed as angled from -180 to 180|
| `dr_mode`           | Unsigned Char| Flag that indicates beginning of dead reckonging IMU control section of the track.|


### Finite State Machine Diagrams
Each task consists of several states that further subdivide the tasks into smaller operations. As each task is run, its current state is executed and updated based on the state of inter-task variables. This allows each task to execute operations efficiently and cede to other tasks as needed, allowing for cooperative multitasking. 

***INSERT TASK DIAGRAM HERE***

### User Interaction Task
This task handles the operation of the USER button to handle calibration and system startup. 

**States**: 
1. State 0 - Initializes interrupt for USER button attached to pin `PC13`. Prompts user to calibrate IR sensor on dark region.
2. State 1 - Once button is pressed, increments `calibration` share to alert IR task to read sensor for calibrating dark surface. When button is pressed agian, increments `calibration` share to alert IR task to read sensor for calibrating light surface. Prompts user that next button press will start Romi
3. State 2 - When button is pressed, `calibration` share is incremented to inform other tasks that IR sensor calibration is complete.
4. State 3 - When button is pressed, `system_done` flag is set. This notifies other tasks that the system is stopping and all tasks will cease operations on their next call.
5. State 4 - Idle state after system stops.

### Actuation Task
This task handles the operation of the encoders and motors to set the motor efforts and update the encoder periodically.

**States**: 
1. State 0 - Initialization state where motors are enabled.
2. State 1 - Check `system_done` flag status. If set, disable motors and set motor PWM effort to 0. If IR calibration is complete (`calibration = 3`) and dead reckoning mode has not begun yet, then update left and right encoders and set motor PWM based on the `R_pwm_effort` and `L_pwm_effort` shares. These shares are set by the controller task to change the motor PWM.
3. State 2 - Idle state after system stops. 

### IR Task
This task handles the operation of the IR sensor to calibrate the sensor and read the centroid of the sensor.

**States**: 
1. State 0 - Disables IR sensor to conserve power. 
2. State 1 - If `calibration` reads 1, read the state of the IR sensor and save it as the `darkValue`. Prints collected `darkValue` to user.
3. State 2 - If `calibration` reads 2, read the state of the IR sensor and save it as the `lightValue`. Prints collected `lightValue` to user.
4. State 3 - If `calibration` reads 3 (fully complete), then update the IR sensor value and update the `centroid` share with the new IR sensor values.
5. State 4 - Idle state after system stops
   
### Controller Task
This task is the control system that ensures the Romi stays on the line during the line following sections. The controller uses the center sensor 7 of the IR array as the reference value for the controller. The measured value for the controller's closed loop feedback is the current centroid of the IR sensor. The centroid represents the point on the IR array that reads the darkest. Based on the centroid, a motor PWM is calculated for the left and right motors. Additionally, this task checks for when Romi has reached the diamond section of the course. When Romi's heading readches ~90°, the controller changes dynamically to use the IMU heading of 90° as the new reference and IMU Euler angles as the measured value. This dynamic swap between line following and IMU heading control is to allow fr more aggressive line following. The more aggressive line follower is not capable of completing the sharp diamond turns due to Romi moving too fast to make corrections. With IMU heading control, we bypass the diamond section by driving straight through it and continuing with line following after.

**States**: 
1. State 0 - Waits for IR calibration to complete then initializes the `motor_controller` object.
2. State 1 - Update Romi's heading using the IMU. If diamond has not passed, check if heading is ~90°. If it is, record encoder position and set the `diamond` flag. If Romi is in `diamond_mode` use IMU proportional control for a set amount of wheel rotations. If `diamond_mode` is not enabled, revert to PI control using the IR sensor.
3. State 2 - Idle state after system stops

### Dead Reckoning Task
This task facilitates the movement through the non-line sections of the course. Each segment of the dead rechoning is preset based on experimentation. The different line segments of the pattern can be seen in the Annotated Game Track in the Project Objective section. 
1. State 0 - Wait for IR calibration to complete. When `calibration` = 3, record the heading of the Romi using the IMU. This heading will serve as the reference angle for all future movements, essentially creating a 
---

