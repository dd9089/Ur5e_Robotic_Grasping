#!/bin/bash

echo "========================================================================"
echo "Activating Trajectory Controller"
echo "========================================================================"
echo ""
echo "This will activate the scaled_joint_trajectory_controller"
echo "Wait for robot driver to be fully started before running this!"
echo ""
echo "========================================================================"
echo ""

cd ~/ur5e/robotiq_gripper_ur5e
source /opt/ros/humble/setup.bash
source install/setup.bash

# Wait a moment for the controller manager to be ready
sleep 2

echo "Switching to scaled_joint_trajectory_controller..."
ros2 control switch_controllers --activate scaled_joint_trajectory_controller

if [ $? -eq 0 ]; then
    echo ""
    echo "✓ Controller activated successfully!"
    echo ""
else
    echo ""
    echo "✗ Failed to activate controller. Make sure robot driver is running."
    echo ""
    exit 1
fi
