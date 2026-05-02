# UR5e + Robotiq 2F-85 Gripper — MoveIt Setup

ROS 2 Humble workspace for controlling a UR5e robot arm with a Robotiq 2F-85 gripper using MoveIt 2.

## Prerequisites

- Ubuntu 22.04 with ROS 2 Humble
- UR5e robot reachable on the network (default IP: `192.168.131.143`)
- Robotiq 2F-85 gripper connected to the UR5e tool connector
- UR Teach Pendant settings:
  - **Tool Communication**: Enabled — 115200 baud, no parity, 1 stop bit
  - **Tool Voltage**: 24V

## Build

```bash
cd ~/ur5e/robotiq_gripper_ur5e
source /opt/ros/humble/setup.bash
colcon build --symlink-install
```

---

## Running the System

You need **3 terminals**. Each step must stay running — do not Ctrl+C until you are done.

### Terminal 1 — Robot Driver + MoveIt + RViz

```bash
cd ~/ur5e/robotiq_gripper_ur5e
./1_start_robot_moveit.sh
```

Wait ~15 seconds for all nodes to initialize. You should see RViz open with the robot model. This also starts the tool communication bridge (`/tmp/ttyUR`) needed by the gripper.

### Terminal 2 — Activate Arm Controller

```bash
cd ~/ur5e/robotiq_gripper_ur5e
./2_activate_controller.sh
```

You should see `✓ Controller activated successfully!`. The arm is now ready for MoveIt commands.

### Terminal 3 — Start Gripper

```bash
cd ~/ur5e/robotiq_gripper_ur5e
source /opt/ros/humble/setup.bash
source install/setup.bash
ros2 launch ur5e_vision_config robotiq_gripper.launch.py
```

Wait for the gripper to activate (you'll hear it cycle open/close once). Keep this terminal running.

---

## Using MoveIt (RViz)

Once all 3 terminals are running:

1. In RViz, use the **interactive marker** (drag the blue/orange ball at the end-effector) to set a goal pose
2. Click **Plan** to compute a trajectory
3. Click **Execute** to move the robot
4. Or click **Plan & Execute** to do both in one step

---

## Controlling the Gripper from Terminal

```bash
# Fully close the gripper
ros2 action send_goal /gripper/robotiq_gripper_controller/gripper_cmd \
  control_msgs/action/GripperCommand \
  "{command: {position: 0.7929, max_effort: 50.0}}"

# Fully open the gripper
ros2 action send_goal /gripper/robotiq_gripper_controller/gripper_cmd \
  control_msgs/action/GripperCommand \
  "{command: {position: 0.0, max_effort: 50.0}}"

# Partially close (any value from 0.0 to 0.7929)
ros2 action send_goal /gripper/robotiq_gripper_controller/gripper_cmd \
  control_msgs/action/GripperCommand \
  "{command: {position: 0.4, max_effort: 50.0}}"
```

- **`position: 0.0`** = fully open
- **`position: 0.7929`** = fully closed
- **`max_effort`** = grip force

## Check Gripper State

```bash
ros2 topic echo /joint_states --once | grep -A2 robotiq
```

---

## Stopping Everything

```bash
cd ~/ur5e/robotiq_gripper_ur5e
./kill_all.sh
```

---

## Motion Speed Configuration

Default velocity and acceleration are set to **10% of maximum** for safe operation.

Edit `src/ur5e_vision_config/config/move_group.yaml`:

```yaml
move_group:
  ros__parameters:
    default_velocity_scaling_factor: 0.1   # 0.0–1.0
    default_acceleration_scaling_factor: 0.1   # 0.0–1.0
```

After changing, rebuild:

```bash
colcon build --packages-select ur5e_vision_config
```

---

## System Status Check

```bash
# List active ROS nodes
ros2 node list

# List controllers and their states
ros2 control list_controllers

# Check key topics
ros2 topic list | grep -E "(planning_scene|joint_states|gripper)"
```

---

## Troubleshooting

| Problem | Fix |
|---|---|
| Controller won't activate | Wait longer for robot driver to fully start, then re-run `./2_activate_controller.sh` |
| Gripper "No such file or directory" | Robot driver (Terminal 1) must be running first — it creates `/tmp/ttyUR` |
| Gripper "Requested 8 bytes, got 0" | Check UR Teach Pendant: Tool Communication enabled, 115200 baud, Tool Voltage 24V |
| Robot won't move in MoveIt | Ensure controller is activated (Terminal 2) and robot is in Remote Control mode on pendant |
| Jerky motion | Verify `ompl_planning.yaml` has Ruckig in response_adapters; check `move_group.yaml` scaling factors |
| MoveIt planning fails | Restart all: `./kill_all.sh` then start from Terminal 1 again |

---

## Project Structure

```
robotiq_gripper_ur5e/
├── 1_start_robot_moveit.sh        # Launch robot driver + MoveIt + RViz
├── 2_activate_controller.sh       # Activate arm trajectory controller
├── kill_all.sh                    # Stop all ROS processes
└── src/
    └── ur5e_vision_config/
        ├── config/
        │   ├── move_group.yaml            # Velocity/acceleration scaling
        │   ├── ompl_planning.yaml         # Motion planner + smoothing config
        │   ├── joint_limits.yaml          # MoveIt joint limits
        │   ├── kinematics.yaml            # IK solver config
        │   ├── moveit_controllers_real.yaml
        │   ├── robotiq_controllers.yaml
        │   └── ur5e/                      # UR5e-specific parameters
        ├── launch/
        │   ├── ur5e_robotiq_real.launch.py   # Main launch file
        │   └── robotiq_gripper.launch.py     # Gripper-only launch
        ├── urdf/
        │   ├── ur5e_with_robotiq.urdf.xacro  # Combined robot + gripper URDF
        │   └── robotiq_standalone.urdf.xacro
        └── srdf/
            └── ur5e_robotiq.srdf.xacro       # MoveIt semantic description
```
