#!/bin/bash

echo "========================================================================"
echo "Killing All UR5e Vision System Processes"
echo "========================================================================"
echo ""

echo "Killing ROS 2 processes..."
pkill -9 -f ros2

echo "Killing Python processes..."
pkill -9 -f "python3.*apriltag"

echo "Killing RViz..."
pkill -9 -f rviz2

echo "Killing collision scene publisher..."
pkill -9 collision_scene_publisher

echo "Killing move_group..."
pkill -9 -f move_group

echo "Killing UR robot driver..."
pkill -9 -f ur_robot_driver

sleep 2

echo ""
echo "Verifying all processes stopped..."
REMAINING=$(ps aux | grep -E "(ros2|rviz2|move_group|apriltag|collision_scene|ur_robot)" | grep -v grep | grep -v kill_all | wc -l)

if [ $REMAINING -eq 0 ]; then
    echo "✓ All processes stopped successfully!"
else
    echo "⚠ Warning: $REMAINING processes still running"
    echo ""
    echo "Remaining processes:"
    ps aux | grep -E "(ros2|rviz2|move_group|apriltag|collision_scene|ur_robot)" | grep -v grep | grep -v kill_all
fi

echo ""
echo "========================================================================"
