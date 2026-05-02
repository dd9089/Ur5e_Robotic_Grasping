from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription, TimerAction
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.substitutions import FindPackageShare
from launch_ros.actions import Node


def generate_launch_description():
    declared_arguments = []
    
    declared_arguments.append(
        DeclareLaunchArgument(
            "robot_ip",
            default_value="10.1.6.79",
            description="IP address of the robot",
        )
    )

    robot_ip = LaunchConfiguration("robot_ip")

    # Launch UR robot driver
    ur_control_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([
            PathJoinSubstitution([
                FindPackageShare("ur_robot_driver"),
                "launch",
                "ur_control.launch.py"
            ])
        ]),
        launch_arguments={
            "ur_type": "ur5e",
            "robot_ip": robot_ip,
            "use_fake_hardware": "false",
            "launch_rviz": "false",
            "description_file": "ur5e_with_marker_holder.urdf.xacro",
            "description_package": "ur5e_vision_config",
            "controllers_file": "ur_controllers.yaml",
            "runtime_config_package": "ur5e_vision_config",
        }.items(),
    )

    # Launch MoveIt with RViz
    # Note: joint_limits.yaml is in ur5e_vision_config/config/ur5e/ folder
    # Note: ompl_planning.yaml uses Ruckig for smooth jerk-limited trajectories
    # Note: Velocity/acceleration scaling set to 10% for slow smooth motion
    moveit_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([
            PathJoinSubstitution([
                FindPackageShare("ur_moveit_config"),
                "launch",
                "ur_moveit.launch.py"
            ])
        ]),
        launch_arguments={
            "ur_type": "ur5e",
            "launch_rviz": "true",
            "description_file": "ur5e_with_marker_holder.urdf.xacro",
            "description_package": "ur5e_vision_config",
        }.items(),
    )

    # Collision scene publisher - loads table collision object
    # Delayed to ensure move_group is ready
    collision_scene_publisher = TimerAction(
        period=5.0,
        actions=[
            Node(
                package="ur5e_vision_config",
                executable="collision_scene_publisher",
                name="collision_scene_publisher",
                output="screen",
            )
        ]
    )

    return LaunchDescription(declared_arguments + [
        ur_control_launch, 
        moveit_launch,
        collision_scene_publisher
    ])
