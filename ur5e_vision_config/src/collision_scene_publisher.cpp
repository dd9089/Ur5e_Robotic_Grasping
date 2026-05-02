#include <rclcpp/rclcpp.hpp>
#include <moveit_msgs/msg/planning_scene.hpp>
#include <moveit_msgs/msg/collision_object.hpp>
#include <shape_msgs/msg/solid_primitive.hpp>
#include <geometry_msgs/msg/pose.hpp>

class CollisionScenePublisher : public rclcpp::Node
{
public:
  CollisionScenePublisher() : Node("collision_scene_publisher"), publish_count_(0)
  {
    auto qos = rclcpp::QoS(10).transient_local();
    scene_pub_ = this->create_publisher<moveit_msgs::msg::PlanningScene>(
      "/planning_scene", qos);
    
    timer_ = this->create_wall_timer(
      std::chrono::seconds(2),
      std::bind(&CollisionScenePublisher::publishScene, this));
    
    RCLCPP_INFO(this->get_logger(), "Collision scene publisher started");
  }

private:
  void publishScene()
  {
    if (publish_count_ > 15) {
      return;
    }
    
    moveit_msgs::msg::PlanningScene planning_scene;
    planning_scene.is_diff = true;
    planning_scene.robot_state.is_diff = true;
    
    // Create table collision object
    moveit_msgs::msg::CollisionObject table;
    table.header.frame_id = "base_link";
    table.id = "table";
    
    shape_msgs::msg::SolidPrimitive table_primitive;
    table_primitive.type = shape_msgs::msg::SolidPrimitive::BOX;
    table_primitive.dimensions.resize(3);
    table_primitive.dimensions[0] = 2.0;  // 2m x
    table_primitive.dimensions[1] = 2.0;  // 2m y
    table_primitive.dimensions[2] = 0.05; // 5cm thick
    
    geometry_msgs::msg::Pose table_pose;
    table_pose.position.x = 0.0;
    table_pose.position.y = 0.0;
    table_pose.position.z = -0.05; // Below base_link
    table_pose.orientation.w = 1.0;
    
    table.primitives.push_back(table_primitive);
    table.primitive_poses.push_back(table_pose);
    table.operation = moveit_msgs::msg::CollisionObject::ADD;
    
    planning_scene.world.collision_objects.push_back(table);
    
    scene_pub_->publish(planning_scene);
    publish_count_++;
    
    if (publish_count_ == 1) {
      RCLCPP_INFO(this->get_logger(), "Table collision object published");
    }
  }

  rclcpp::Publisher<moveit_msgs::msg::PlanningScene>::SharedPtr scene_pub_;
  rclcpp::TimerBase::SharedPtr timer_;
  int publish_count_;
};

int main(int argc, char** argv)
{
  rclcpp::init(argc, argv);
  rclcpp::spin(std::make_shared<CollisionScenePublisher>());
  rclcpp::shutdown();
  return 0;
}
