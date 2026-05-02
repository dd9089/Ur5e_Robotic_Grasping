cmake_minimum_required(VERSION 3.8)
project(ur5e_vision_config)

if(CMAKE_COMPILER_IS_GNUCXX OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")
  add_compile_options(-Wall -Wextra -Wpedantic)
endif()

# find dependencies
find_package(ament_cmake REQUIRED)
find_package(moveit_ros_planning_interface REQUIRED)
find_package(rclcpp REQUIRED)
find_package(geometry_msgs REQUIRED)
find_package(tf2_ros REQUIRED)
find_package(moveit_msgs REQUIRED)
find_package(shape_msgs REQUIRED)

# Build apriltag_tf_broadcaster
add_executable(apriltag_tf_broadcaster src/apriltag_tf_broadcaster.cpp)
ament_target_dependencies(apriltag_tf_broadcaster
  rclcpp
  geometry_msgs
  tf2_ros
)

# Build collision_scene_publisher
add_executable(collision_scene_publisher src/collision_scene_publisher.cpp)
ament_target_dependencies(collision_scene_publisher
  rclcpp
  moveit_msgs
  shape_msgs
  geometry_msgs
)

# Build static_scene_publisher
add_executable(static_scene_publisher src/static_scene_publisher.cpp)
ament_target_dependencies(static_scene_publisher
  rclcpp
  moveit_msgs
  shape_msgs
  geometry_msgs
)

# Install executables
install(TARGETS
  apriltag_tf_broadcaster
  collision_scene_publisher
  static_scene_publisher
  DESTINATION lib/${PROJECT_NAME}
)

# Install launch files
install(DIRECTORY launch
  DESTINATION share/${PROJECT_NAME}/
)

# Install urdf files
install(DIRECTORY urdf
  DESTINATION share/${PROJECT_NAME}/
)

# Install rviz files
install(DIRECTORY rviz
  DESTINATION share/${PROJECT_NAME}/
)

# Install srdf files
install(DIRECTORY srdf
  DESTINATION share/${PROJECT_NAME}/
)

# Install config files
install(DIRECTORY config
  DESTINATION share/${PROJECT_NAME}/
)

# Install mesh files
install(DIRECTORY meshes
  DESTINATION share/${PROJECT_NAME}/
)

# Install resources (custom URScript templates)
install(DIRECTORY resources
  DESTINATION share/${PROJECT_NAME}/
)

if(BUILD_TESTING)
  find_package(ament_lint_auto REQUIRED)
  set(ament_cmake_copyright_FOUND TRUE)
  set(ament_cmake_cpplint_FOUND TRUE)
  ament_lint_auto_find_test_dependencies()
endif()

ament_package()
