"""
Standalone Robotiq 2F-85 gripper launch file for real hardware.

This launch file:
1. Starts the gripper ros2_control_node (socat bridge is handled by UR driver
   when use_tool_communication:=true, creating /tmp/ttyUR automatically)
2. Spawns the gripper controllers (kept alive to unload on shutdown)

Prerequisites:
  - UR driver must be running with use_tool_communication:=true
  - Play must be pressed on the teach pendant
  - /tmp/ttyUR must exist (created by UR driver's tool_communication node)

Usage:
  Terminal 1: ros2 launch ur5e_vision_config ur5e_robotiq_real.launch.py
  (press Play on teach pendant)
  Terminal 2: ros2 launch ur5e_vision_config robotiq_gripper.launch.py
"""
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, TimerAction
from launch.substitutions import Command, FindExecutable, LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():
    com_port_arg = DeclareLaunchArgument(
        "com_port",
        default_value="/tmp/ttyUR",
        description="Serial port for the Robotiq gripper",
    )

    com_port = LaunchConfiguration("com_port")

    robot_description_content = Command(
        [
            PathJoinSubstitution([FindExecutable(name="xacro")]),
            " ",
            PathJoinSubstitution([
                FindPackageShare("ur5e_vision_config"),
                "urdf",
                "robotiq_standalone.urdf.xacro",
            ]),
            " ",
            "use_fake_hardware:=false",
            " ",
            "com_port:=", com_port,
        ]
    )

    robot_description_param = {
        "robot_description": ParameterValue(robot_description_content, value_type=str)
    }

    controllers_file = PathJoinSubstitution(
        [FindPackageShare("ur5e_vision_config"), "config", "robotiq_controllers.yaml"]
    )

    control_node = Node(
        package="controller_manager",
        executable="ros2_control_node",
        namespace="gripper",
        parameters=[robot_description_param, controllers_file],
        remappings=[
            ("joint_states", "/joint_states"),
        ],
        respawn=True,
        respawn_delay=5.0,
        output="screen",
    )

    activation_spawner = TimerAction(
        period=5.0,
        actions=[
            Node(
                package="controller_manager",
                executable="spawner",
                namespace="gripper",
                arguments=[
                    "robotiq_activation_controller",
                    "-c", "/gripper/controller_manager",
                    "--controller-manager-timeout", "120",
                    "--unload-on-kill",
                ],
                output="screen",
            )
        ],
    )

    jsb_spawner = TimerAction(
        period=7.0,
        actions=[
            Node(
                package="controller_manager",
                executable="spawner",
                namespace="gripper",
                arguments=[
                    "gripper_joint_state_broadcaster",
                    "-c", "/gripper/controller_manager",
                    "--controller-manager-timeout", "120",
                    "--unload-on-kill",
                ],
                output="screen",
            )
        ],
    )

    gripper_spawner = TimerAction(
        period=10.0,
        actions=[
            Node(
                package="controller_manager",
                executable="spawner",
                namespace="gripper",
                arguments=[
                    "robotiq_gripper_controller",
                    "-c", "/gripper/controller_manager",
                    "--controller-manager-timeout", "120",
                    "--unload-on-kill",
                ],
                output="screen",
            )
        ],
    )

    return LaunchDescription([
        com_port_arg,
        control_node,
        activation_spawner,
        jsb_spawner,
        gripper_spawner,
    ])
