#include <rclcpp/rclcpp.hpp>
#include <moveit_msgs/msg/planning_scene.hpp>
#include <moveit_msgs/msg/collision_object.hpp>
#include <shape_msgs/msg/solid_primitive.hpp>
#include <geometry_msgs/msg/pose.hpp>

class StaticScenePublisher : public rclcpp::Node
{
public:
  StaticScenePublisher() : Node("static_scene_publisher")
  {
    // Publisher for planning scene
    scene_pub_ = this->create_publisher<moveit_msgs::msg::PlanningScene>(
      "/planning_scene", rclcpp::QoS(10).transient_local());
    
    // Wait a moment for move_group to be ready
    rclcpp::sleep_for(std::chrono::seconds(2));
    
    // Publish the static scene
    publishStaticScene();
    
    RCLCPP_INFO(this->get_logger(), "Static planning scene published");
  }

private:
  void publishStaticScene()
  {
    moveit_msgs::msg::PlanningScene planning_scene;
    planning_scene.is_diff = true;
    
    // Table collision object (2m x 2m x 50mm, at base mounting plate level)
    moveit_msgs::msg::CollisionObject table;
    table.header.frame_id = "world";
    table.id = "table";
    
    shape_msgs::msg::SolidPrimitive table_primitive;
    table_primitive.type = shape_msgs::msg::SolidPrimitive::BOX;
    table_primitive.dimensions = {2.0, 2.0, 0.05};  // 2m x 2m x 50mm
    
    geometry_msgs::msg::Pose table_pose;
    table_pose.position.x = 0.0;
    table_pose.position.y = 0.0;
    table_pose.position.z = 0.020;  // Center at +24mm (bottom at -1mm, slight gap to avoid collision)
    table_pose.orientation.w = 1.0;
    
    table.primitives.push_back(table_primitive);
    table.primitive_poses.push_back(table_pose);
    table.operation = moveit_msgs::msg::CollisionObject::ADD;
    
    planning_scene.world.collision_objects.push_back(table);
    
    // Publish scene
    scene_pub_->publish(planning_scene);
    
    RCLCPP_INFO(this->get_logger(), "Static planning scene published (table collision object)");
  }

  rclcpp::Publisher<moveit_msgs::msg::PlanningScene>::SharedPtr scene_pub_;
};

int main(int argc, char** argv)
{
  rclcpp::init(argc, argv);
  auto node = std::make_shared<StaticScenePublisher>();
  
  // Keep node alive briefly then exit
  rclcpp::sleep_for(std::chrono::seconds(1));
  
  rclcpp::shutdown();
  return 0;
}
