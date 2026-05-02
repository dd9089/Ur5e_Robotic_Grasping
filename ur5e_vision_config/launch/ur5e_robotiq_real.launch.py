import os

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription, OpaqueFunction, TimerAction
from launch.substitutions import Command, FindExecutable, LaunchConfiguration, PathJoinSubstitution
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue
from launch_ros.substitutions import FindPackageShare
from ur_moveit_config.launch_common import load_yaml


def launch_setup(context, *args, **kwargs):
    robot_ip = LaunchConfiguration("robot_ip")

    # --- UR Robot Driver (real hardware) ---
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
            "description_file": "ur5e_with_robotiq.urdf.xacro",
            "description_package": "ur5e_vision_config",
            "controllers_file": "ur_controllers.yaml",
            "runtime_config_package": "ur5e_vision_config",
            "initial_joint_controller": "scaled_joint_trajectory_controller",
            "activate_joint_controller": "true",
            "use_tool_communication": "true",
            "tool_device_name": "/tmp/ttyUR",
            "tool_tcp_port": "54321",
            "tool_voltage": "24",
            "tool_parity": "0",
            "tool_baud_rate": "115200",
            "tool_stop_bits": "1",
            "tool_rx_idle_chars": "1.5",
            "tool_tx_idle_chars": "3.5",
            "controller_manager_timeout": "120",
        }.items(),
    )

    # --- MoveIt move_group (configured for real hardware) ---

    description_package = "ur5e_vision_config"
    joint_limit_params = PathJoinSubstitution(
        [FindPackageShare(description_package), "config", "ur5e", "joint_limits.yaml"]
    )
    kinematics_params = PathJoinSubstitution(
        [FindPackageShare(description_package), "config", "ur5e", "default_kinematics.yaml"]
    )
    physical_params = PathJoinSubstitution(
        [FindPackageShare(description_package), "config", "ur5e", "physical_parameters.yaml"]
    )
    visual_params = PathJoinSubstitution(
        [FindPackageShare(description_package), "config", "ur5e", "visual_parameters.yaml"]
    )

    robot_description_content = Command(
        [
            PathJoinSubstitution([FindExecutable(name="xacro")]),
            " ",
            PathJoinSubstitution([FindPackageShare(description_package), "urdf", "ur5e_with_robotiq.urdf.xacro"]),
            " ",
            "robot_ip:=", robot_ip,
            " ",
            "joint_limit_params:=", joint_limit_params,
            " ",
            "kinematics_params:=", kinematics_params,
            " ",
            "physical_params:=", physical_params,
            " ",
            "visual_params:=", visual_params,
            " ",
            "name:=ur",
            " ",
            "ur_type:=ur5e",
            " ",
            "use_fake_hardware:=false",
            " ",
            "com_port:=/tmp/ttyUR",
            " ",
            "script_filename:=ros_control.urscript",
            " ",
            "input_recipe_filename:=rtde_input_recipe.txt",
            " ",
            "output_recipe_filename:=rtde_output_recipe.txt",
            " ",
            "prefix:=",
            " ",
        ]
    )
    robot_description = {
        "robot_description": ParameterValue(robot_description_content, value_type=str)
    }

    # Semantic description (SRDF)
    robot_description_semantic_content = Command(
        [
            PathJoinSubstitution([FindExecutable(name="xacro")]),
            " ",
            PathJoinSubstitution([FindPackageShare(description_package), "srdf", "ur5e_robotiq.srdf.xacro"]),
            " ",
            "name:=ur",
            " ",
            'prefix:=""',
            " ",
        ]
    )
    robot_description_semantic = {
        "robot_description_semantic": ParameterValue(robot_description_semantic_content, value_type=str)
    }

    # Kinematics
    robot_description_kinematics = PathJoinSubstitution(
        [FindPackageShare(description_package), "config", "kinematics.yaml"]
    )

    # Joint limits for MoveIt planning
    robot_description_planning = {
        "robot_description_planning": load_yaml(description_package, "config/joint_limits.yaml")
    }

    # Move group parameters (velocity/acceleration scaling)
    move_group_params = load_yaml(description_package, "config/move_group.yaml")

    # OMPL planning pipeline
    ompl_planning_yaml = load_yaml(description_package, "config/ompl_planning.yaml")
    ompl_planning_pipeline_config = {
        "move_group": {
            "planning_plugin": "ompl_interface/OMPLPlanner",
            "request_adapters": (
                "default_planner_request_adapters/AddTimeOptimalParameterization "
                "default_planner_request_adapters/FixWorkspaceBounds "
                "default_planner_request_adapters/FixStartStateBounds "
                "default_planner_request_adapters/FixStartStateCollision "
                "default_planner_request_adapters/FixStartStatePathConstraints"
            ),
            "start_state_max_bounds_error": 0.1,
        }
    }
    ompl_planning_pipeline_config["move_group"].update(ompl_planning_yaml)

    # MoveIt controllers - scaled_joint_trajectory_controller as default for real hardware
    controllers_yaml = load_yaml(description_package, "config/moveit_controllers_real.yaml")
    moveit_controllers = {
        "moveit_simple_controller_manager": controllers_yaml,
        "moveit_controller_manager": "moveit_simple_controller_manager/MoveItSimpleControllerManager",
    }

    # Trajectory execution
    trajectory_execution = {
        "moveit_manage_controllers": False,
        "trajectory_execution.allowed_execution_duration_scaling": 1.2,
        "trajectory_execution.allowed_goal_duration_margin": 0.5,
        "trajectory_execution.allowed_start_tolerance": 0.01,
        "trajectory_execution.execution_duration_monitoring": False,
    }

    planning_scene_monitor_parameters = {
        "publish_planning_scene": True,
        "publish_geometry_updates": True,
        "publish_state_updates": True,
        "publish_transforms_updates": True,
    }

    warehouse_ros_config = {
        "warehouse_plugin": "warehouse_ros_sqlite::DatabaseConnection",
        "warehouse_host": os.path.expanduser("~/.ros/warehouse_ros.sqlite"),
    }

    # move_group node
    move_group_node = Node(
        package="moveit_ros_move_group",
        executable="move_group",
        output="screen",
        parameters=[
            robot_description,
            robot_description_semantic,
            {"publish_robot_description_semantic": True},
            robot_description_kinematics,
            robot_description_planning,
            ompl_planning_pipeline_config,
            trajectory_execution,
            moveit_controllers,
            planning_scene_monitor_parameters,
            move_group_params,
            {"use_sim_time": False},
            warehouse_ros_config,
        ],
    )

    # RViz with MoveIt config
    rviz_config_file = PathJoinSubstitution(
        [FindPackageShare(description_package), "rviz", "view_robot.rviz"]
    )
    rviz_node = Node(
        package="rviz2",
        executable="rviz2",
        name="rviz2_moveit",
        output="log",
        arguments=["-d", rviz_config_file],
        parameters=[
            robot_description,
            robot_description_semantic,
            ompl_planning_pipeline_config,
            robot_description_kinematics,
            robot_description_planning,
            warehouse_ros_config,
        ],
    )

    # Collision scene publisher - loads table collision object
    collision_scene_publisher = TimerAction(
        period=10.0,
        actions=[
            Node(
                package="ur5e_vision_config",
                executable="collision_scene_publisher",
                name="collision_scene_publisher",
                output="screen",
            )
        ]
    )

    return [
        ur_control_launch,
        move_group_node,
        rviz_node,
        collision_scene_publisher,
    ]


def generate_launch_description():
    declared_arguments = []

    declared_arguments.append(
        DeclareLaunchArgument(
            "robot_ip",
            default_value="192.168.131.143",
            description="IP address of the robot",
        )
    )

    return LaunchDescription(declared_arguments + [OpaqueFunction(function=launch_setup)])
