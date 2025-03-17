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

3. **Motor Characterization**: The motors we used were characterized reading from encoder.py and running them at various PWM. We implemented motor characterization for the ROMI by measuring each motor’s time constant, gain, and startup effort. We analyzed position and velocity step responses up to 70% PWM, confirming that one motor runs slightly faster in a straight line. This reinforced our hypothesis that we need a controller to be used for every ROMI movement command in order to maintain balanced, accurate control of the robot. We implemented control either through IMU-based heading correction or line-based using the infrared sensor feedback.
   
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

<img width="486" alt="Screenshot 2025-03-16 at 2 51 15 PM" src="https://github.com/user-attachments/assets/5fd8c64f-42b5-4e0d-bd6d-4b6901044f52" />

**Figure 6.** Steady-State Velocity of Left Motor at PWM Step Input Ranging from 0-70% showing Motor Gain and Startup Effort 

<img width="535" alt="Screenshot 2025-03-16 at 2 47 28 PM" src="https://github.com/user-attachments/assets/bead682e-726b-4d20-85d6-142150f10ccf" />

**Figure 7.** Linearized Step Responses for the Right Motor at Various PWM Efforts ranging from 10–70% Overlaid with a Global Best-Fit Line (τ ≈ 0.074 s) for the Motor Step Response Experiment. 

<img width="535" alt="Screenshot 2025-03-16 at 2 47 54 PM" src="https://github.com/user-attachments/assets/056e3095-c60b-40cf-94a2-c145ab76bcdb" />

**Figure 8.** Linearized Step Responses for the Left Motor at Various PWM Efforts ranging from 10–70% Overlaid with a Global Best-Fit Line (τ ≈ 0.077 s) for the Motor Step Response Experiment. 

 **Discussion**: From the figures, both motors share similar dynamics but they have different velocity and slip. The right motor runs marginally faster at the same PWM and stops less smoothly, suggesting unequal friction or mechanical wear. These deviations highlight the need for closed-loop control that automatically corrects for motor-to-motor differences.

 

## Firmware Design Overview
1. **Hardware Drivers**: Each hardware component—motors, sensors, encoders, and the IMU—is managed by a dedicated driver that encapsulates the microcontroller’s low-level specifics (pin assignments, registers, timers, etc.). By providing clear, high-level methods, these drivers hide the intricate setup details from the rest of the codebase. This approach keeps the system modular and maintainable: if hardware pins or peripherals change, only the corresponding driver needs updating, while the rest of the application remains unaffected. It also streamlines debugging and testing, because each component’s functionality can be verified in isolation without juggling microcontroller minutiae in every part of the project.
   
2. **Line Following**: The robot features an array of IR sensors arranged to detect the difference in reflectivity between the line and surrounding surface. By sampling each sensor’s value, the code computes a “centroid” of reflectance, effectively determining the line’s relative position. A simple PI controller (proportional, integral terms) then adjusts motor speeds to steer the robot back toward the line’s center. This setup allows the robot to smoothly track curves and handle minor deviations, ensuring continuous, stable line following across varying course layouts.
   
3. **Heading Control**: A BNO055 IMU provides real-time heading data (Euler angles), enabling more advanced maneuvers beyond standard line following. The robot’s code compares this heading to a desired reference angle, and a controller applies proportional corrections to the motor outputs. This approach lets the robot rotate to precise angles—such as 90° for “diamond mode” or 180° for reversing—without relying solely on line-sensing. By decoupling orientation from visual tracks, the system remains robust even when the line is missing or deliberately ignored (e.g., during dead-reckoning segments).
   
4. **Cooperative Multitasking**: The system is organized into distinct tasks—such as IR sensor readings, motor control, and user interaction—each running in a cooperative scheduler (via cotask.py and task_share.py). Rather than use a traditional preemptive RTOS, this approach allows each task to execute sequentially, yielding control back to the scheduler when finished. As a result, the robot remains responsive while the codebase stays modular, making it easier to debug individual tasks and manage shared data without complex thread-synchronization overhead.

## Hardware Drivers
### BNO055
The `BNO055` driver is designed to interface with the BNO055 sensor over I2C using the `pyb` module. It handles sensor initialization, data acquisition (e.g., Euler angles and gyroscope data), calibration management, and heading correction.

**Initialization and Setup**
- **`__init__(self, i2c, address=0x28)`**  
  - Initializes the sensor with a given I2C instance.
  - Reads and verifies the CHIP_ID against an expected value.
  - Sets the sensor to CONFIGMODE for configuration, then switches to NDOF_MODE.
  - Initializes a heading offset to zero.

**Private Register Access Methods**
- `_read_register(self, reg, nbytes=1)`: Reads a specified number of bytes starting from a given register.
- `_write_register(self, reg, data)`: Writes data (integer or bytearray) to a specified register.

**Mode Management and Calibration**
- `set_mode(self, mode)`: Updates the sensor’s operating mode by writing to the OPR_MODE register, with a delay to allow the mode change.
- `get_calibration_status(self)`: Reads the calibration status byte and parses it into individual components for the system, gyro, accelerometer, and magnetometer.
- `get_calibration_coefficients(self)`: Retrieves 22 bytes of calibration data from the sensor.
- `set_calibration_coefficients(self, coeffs)`: Writes a 22-byte calibration dataset back to the sensor. Raises a `ValueError` if the provided data is not 22 bytes long.

**Data Acquisition Methods**
- `read_euler_angles(self)`: Reads raw Euler angle data (currently implemented for heading) from the sensor. Converts the raw two-byte data into a heading using a scale factor.
- `read_angular_velocity(self)`: Reads 6 bytes of gyroscope data and converts them to angular velocity values (x, y, z) using an example scale factor.

**Heading Correction and Error Computation**
- `set_offset(self)`: Captures the current heading to use as an offset for subsequent corrections.
- `get_corrected_heading(self)`: Returns the heading corrected by subtracting the stored offset and normalizing it to the 0°–360° range.
- `compute_heading_error(self, target_heading)`: Computes the minimal angular error between the corrected heading and a target heading, yielding a value in the range -180° to +180°.

### Motor
The `Motor` driver is designed to interface with motor controllers using separate PWM and direction signals via the `pyb` module. It provides methods for motor initialization, effort control, and power management.

**Initialization and Setup**
- `__init__(self, PWM, DIR, nSLP, TimerChannel)`
  - Initializes the Motor object by configuring the sleep (nSLP) and direction (DIR) pins.
  - Sets up Timer 1 at a 20 kHz frequency and initializes a PWM channel on the specified timer channel with an initial pulse width of 0%.
  - Initializes the motor's effort to zero.

**Effort Control**
- `set_effort(self, effort)`
  - Sets the motor's effort (speed/torque) based on an input value between -100 and 100.
  - For negative values:
    - Sets the motor direction to reverse.
    - Saturates the effort at -45 to avoid slipping
  - For positive values:
    - Sets the motor direction to forward.
    - Caps the effort at 45.
  - For zero effort:
    - Stops the motor by setting the PWM duty cycle to 0.
- `get_effort(self)`
  - Returns the current motor effort value.

**Power Management**
- `enable(self)`
  - Enables the motor driver by setting the sleep (nSLP) pin high (taking it out of sleep mode).
  - Resets the PWM duty cycle to 0.
- `disable(self)`
  - Disables the motor driver by setting the sleep (nSLP) pin low (putting it into sleep mode).
  - Stops PWM output by setting the duty cycle to 0 and deinitializes the timer.

### Encoder
The `Encoder` driver provides a quadrature encoder decoding interface using a hardware timer and GPIO pins. It tracks the encoder's position, computes velocity, and handles counter overflow/underflow for accurate angular measurement.

**Initialization and Setup**
- `__init__(self, tim, chA_pin, chB_pin)`  
  - Initializes the encoder with a specified timer and channel pins for A and B.
  - Configures Timer channels in quadrature encoder mode (`ENC_AB`).
  - Sets up internal state variables including position, previous counter, delta and dt buffers.
  - Defines a conversion factor to translate encoder counts to radians.

**Update and Data Processing**
- `update(self)`  
  - Retrieves the current timer count and current time in microseconds.
  - Calculates the difference in counts from the previous update, adjusting for counter overflow/underflow.
  - Updates rolling buffers for delta counts and time intervals.
  - Computes an average delta from the buffer and updates the total accumulated position.

**Position and Velocity Retrieval**
- `get_position(self)`  
  - Returns the current encoder position converted to radians using the conversion factor.
- `get_velocity(self)`  
  - Calculates the average time interval and position change from the buffers.
  - Returns the angular velocity in radians per second based on the averaged delta and time difference.
- `get_time(self)`  
  - Returns the timestamp of the last update in seconds.
- `get_dt(self)`  
  - Returns the time difference between the last two updates in seconds.

**Resetting the Encoder**
- `zero(self)`  
  - Resets the accumulated encoder position to zero.
  - Updates the reference counter to the current timer counter for future measurements.

### IR Sensor Driver
The IR sensor module provides two classes to handle infrared sensing: `IR_Single` for interfacing with a single IR sensor via ADC, and `IR_Array` for managing an array of IR sensors with calibration, normalization, and centroid computation functionalities.

**IR_Single**
- **Initialization and Setup**
  - `__init__(self, pin, index)`  
    - Configures the specified pin as an input and sets up an ADC for the sensor.
    - Assigns an index identifier and initializes an empty list for storing sensor values.
- **Data Acquisition**
  - `getADC(self)`  
    - Returns the ADC object associated with the sensor.
  - `getValue(self)`  
    - Reads and returns the current ADC value from the IR sensor.

**IR_Array**
- **Initialization and Setup**
  - `__init__(self, irPinList, evenPin, oddPin)`  
    - Instantiates an `IR_Single` object for each pin in the provided list, building the sensor array.
    - Sets up two control pins (`evenPin` and `oddPin`) for sensor enabling (dimming control is noted but not implemented).
    - Initializes internal variables for raw and normalized sensor values, calibration data (dark and light values), and the centroid.
- **Data Acquisition and Normalization**
  - `readArray(self)`  
    - Enables the sensor array, pauses briefly, then reads raw ADC values from each sensor before disabling the array.
  - `normalize(self)`  
    - Converts raw sensor readings into normalized values between 0 and 1 using pre-calibrated dark and light reference values.
- **Sensor Update and Data Retrieval**
  - `updateIR(self)`  
    - Combines reading and normalization steps to update the sensor array and returns the list of normalized values.
  - `getList(self)`  
    - Returns the current list of normalized sensor readings.
  - `getCentroid(self)`  
    - Computes a weighted average (centroid) of the sensor readings, useful for determining the sensor array’s overall response.
- **Calibration**
  - `calibrateDark(self)`  
    - Captures and sets the dark calibration values based on sensor readings.
  - `calibrateLight(self)`  
    - Captures and sets the light calibration values based on sensor readings.
- **Sensor Control**
  - `enable(self)`  
    - Activates the sensor array by setting the control pins high.
  - `disable(self)`  
    - Deactivates the sensor array by setting the control pins low.

### Bump Sensor Driver
The Bump sensor module provides two classes to manage bump sensor inputs using interrupts: `Bumpy` for handling individual bump sensors and `Bumpies` for aggregating multiple bump sensors.

**Bumpy**
- **Initialization and Setup**
  - **`__init__(self, Bump_Pin)`**  
    - Initializes the bump sensor on the specified pin configured as an input with no pull.
    - Attaches an interrupt on the falling edge (with a pull-up configuration) that calls the `bump_interrupt` method.
    - Initializes an internal flag (`HIT`) to track whether a bump event has occurred.
- **Event Handling and Status**
  - **`bump_interrupt(self, line)`**  
    - Interrupt callback that sets the `HIT` flag to `True` when a bump is detected.
  - **`reset_status(self)`**  
    - Resets the `HIT` flag to `False`.
  - **`get_status(self)`**  
    - Returns the current state of the `HIT` flag (i.e., whether a bump event has been registered).

**Bumpies**
- **Initialization and Setup**
  - **`__init__(self, Pin_List)`**  
    - Creates a list of `Bumpy` objects, one for each pin provided in `Pin_List`.
- **Aggregated Sensor State**
  - **`get_status(self)`**  
    - Iterates through all bump sensors and returns `True` if any sensor's `HIT` flag is set.
- **Status Reset**
  - **`reset_status(self)`**  
    - Resets the status of all bump sensors by calling each sensor's `reset_status` method.


## Task Breakdown
To facilitate cooperative multitasking, the different hardware/software operations of Romi were split into different tasks. Each task in charge of operating a different aspect of the system. Our design has 6 tasks:
1. User Interaction
2. Actuation
3. IR
4. Controller
5. Dead Reckoning

### Tasks
Each task runs at a different period and each task is assigned a priority. Some tasks such as Actuation and IR must be run at higher frequencies as their hardaware needs to be manipulated more often. Tasks that are run more frequently are given a lower priority. This allows tasks that run at a lower frequency to take priority in case two tasks with different priorities are called simultaneously. Tasks are created by defining Python generator functions that represent each task. These functions are then used with the `cotask.py` scheduler module to create tasks with defined periods and priorities. Below is a task diagram showing the periods and priorities of each task. Additionally, the transfer of information through inter-task variables is also shown. 

***INSERT TASK DIAGRAM HERE***

### Shares
The transfer of all inter-task variables is done with the `task_share.py`. This module allows the creation `Share` objects that are passed into each task. Each task also has the ability to read and write to the Shares it has access to. Using `Share` objects avoids the use of global variables as inter-task variables.

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
This task handles the robot’s navigation through regions where it must follow pre-planned routes and rotate to specific headings, rather than relying on line following. It uses both the **IMU** (for heading feedback) and **encoders** (for distance tracking) to achieve precise movements. If the robot encounters an obstacle, bump sensors trigger an override sequence that redirects the robot around the wall.

**States**:
1. **State 0** - Waits until IR calibration is finished (i.e., the `calibration` share is set to 3). Once calibration is confirmed, sets the IMU’s offset and moves to the next state.

2. **State 1** - Checks if the robot’s encoders (`encL` and `encR`) have reached certain thresholds, indicating it’s time to switch from normal line following to dead reckoning. Once thresholds are met, `dr_mode` is set to start the dead reckoning sequence.

3. **State 2** - Rotates the robot to the target heading specified in the `route_segments` array. Compares the current heading to the desired heading; if the error is outside the allowed tolerance, the robot turns left or right until aligned. On success, stops motors and transitions to straight driving.

4. **State 3** - Drives forward a specified distance (tracked by encoders) while maintaining a heading lock. If the route segment is marked with `"bump"`, checks for collisions using bump sensors. Upon completing the distance, updates to the next route segment or triggers a bump override if a collision is detected.

5. **State 10+**  
   - Executes a multi-step sequence (reverse, rotate, drive, etc.) to navigate around a wall or obstacle. Each sub-state (1–8) handles a specific maneuver:
     - **Reverse** for a short distance  
     - **Rotate** to a specific heading (0°, -90°, 180°, etc.)  
     - **Drive** forward for a set distance at that heading  
     - Repeat until the full route around the obstacle is complete  
   - Each sub-step uses encoders to measure distance and the IMU to confirm heading accuracy. Once the finish point is reached, sets `system_done` to indicate the robot is done moving.

6. **State 99** - Idle state after system stops

