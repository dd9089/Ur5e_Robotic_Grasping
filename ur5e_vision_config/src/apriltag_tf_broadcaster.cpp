#include <rclcpp/rclcpp.hpp>
#include <tf2_ros/transform_broadcaster.h>
#include <geometry_msgs/msg/transform_stamped.hpp>
#include <geometry_msgs/msg/pose_stamped.hpp>

class AprilTagTFBroadcaster : public rclcpp::Node
{
public:
  AprilTagTFBroadcaster() : Node("apriltag_tf_broadcaster")
  {
    tf_broadcaster_ = std::make_shared<tf2_ros::TransformBroadcaster>(this);
    
    // Subscribe to AprilTag pose topic
    pose_sub_ = this->create_subscription<geometry_msgs::msg::PoseStamped>(
      "/apriltag_pose", 10,
      std::bind(&AprilTagTFBroadcaster::poseCallback, this, std::placeholders::_1));
    
    RCLCPP_INFO(this->get_logger(), "AprilTag TF Broadcaster started");
  }

private:
  void poseCallback(const geometry_msgs::msg::PoseStamped::SharedPtr msg)
  {
    geometry_msgs::msg::TransformStamped transform;
    
    transform.header = msg->header;
    transform.child_frame_id = "apriltag";
    
    transform.transform.translation.x = msg->pose.position.x;
    transform.transform.translation.y = msg->pose.position.y;
    transform.transform.translation.z = msg->pose.position.z;
    
    transform.transform.rotation = msg->pose.orientation;
    
    tf_broadcaster_->sendTransform(transform);
  }

  std::shared_ptr<tf2_ros::TransformBroadcaster> tf_broadcaster_;
  rclcpp::Subscription<geometry_msgs::msg::PoseStamped>::SharedPtr pose_sub_;
};

int main(int argc, char** argv)
{
  rclcpp::init(argc, argv);
  rclcpp::spin(std::make_shared<AprilTagTFBroadcaster>());
  rclcpp::shutdown();
  return 0;
}
