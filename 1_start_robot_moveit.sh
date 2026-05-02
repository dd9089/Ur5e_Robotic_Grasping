#!/bin/bash

echo "========================================================================"
echo "Starting UR5e Robot Driver with MoveIt and RViz"
echo "========================================================================"
echo ""
echo "This will launch:"
echo "  - UR5e robot driver (connected to 10.1.6.226)"
echo "  - MoveIt motion planning"
echo "  - RViz with interactive control"
echo ""
echo "Press Ctrl+C to stop"
echo "========================================================================"
echo ""

export DISPLAY=:0
cd ~/ur5e/robotiq_gripper_ur5e
source /opt/ros/humble/setup.bash
source install/setup.bash

ros2 launch ur5e_vision_config ur5e_robotiq_real.launch.py robot_ip:=192.168.131.143
