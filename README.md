# Line-Following Robot

A mechatronics project that uses an array of infrared sensors, a BNO055 IMU, and cooperative multitasking to follow a predefined course, detect obstacles, and perform special maneuvers. Check out the live demo to see it in action!

**Link to project:** [http://example.com/line-follower-demo](http://example.com/line-follower-demo)

![Line-Following Robot Demo](https://via.placeholder.com/1200x650.png?text=Line+Following+Robot+Demo)

---

## How It's Made:

**Tech used:** MicroPython, IR Sensors, BNO055 IMU, Quadrature Encoders, DC Motors with PWM Control

1. **Mechanical/Electrical Design**  
   *(I will fill this section in.)*

2. **Firmware & Code**  
   - The main program (`main.py`) sets up cooperative tasks (line following, IMU-based mode, dead reckoning, etc.).  
   - **Line Following**: The IR sensor array readings are normalized, and a centroid is calculated for steering.  
   - **Heading Control**: The IMU data is used for special maneuvers where line following breaks down. A nominal heading is calculated   and proportional control is aplied to ensure heading is kept.
   - **Dead-Reckoning**: Once certain checkpoints are reached, the robot drives using encoder feedback to hit target distances.  
   - **Cooperative Multitasking**: Code is organized into tasks for cleanliness, each handling a specific subsystem. 

---

## Optimizations

- **PID Tuning**  
  Early prototypes used basic proportional control. Adding integral terms significantly improved stability and reduced overshoot when line following. Derivative control was not applied as it led to unstable behavior. Additionally, IMU control only used proportional control as it was sufficient to keep the desired heading.   

- **Line Sensor Calibration**  
  During startup, the line sensor is placed over a dark patch and light patch to calibrate line sensor array. Each individual emitter/reciever pair is normalized to a range between 0 (light) and 1 (dark). This ensures any erroneous sensors still provide usable data.

- **IMU Sensor Calibration**
  IMU sensor was calibrated following the BNO055 sensor's datasheet instructions. Once the calibration coefficients were determined they were written to the IMU on startup.
  
- **Bump Handling**  
  Interrupt-driven bump sensors allowing immediate response to wall impact
