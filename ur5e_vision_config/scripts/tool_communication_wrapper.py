#!/usr/bin/env python3
"""
Wrapper around socat for tool communication that retries the TCP connection
until port 54321 becomes available (after External Control starts and
set_tool_communication() is called in the URScript).
"""
import subprocess
import time
import sys
import signal

import rclpy
from rclpy.node import Node


class ToolCommunicationWrapper(Node):
    def __init__(self):
        super().__init__("tool_communication_wrapper")

        self.declare_parameter("robot_ip", "192.168.131.143")
        self.declare_parameter("tcp_port", 54321)
        self.declare_parameter("device_name", "/tmp/ttyUR")
        self.declare_parameter("retry_interval", 2.0)

        self.robot_ip = self.get_parameter("robot_ip").get_parameter_value().string_value
        self.tcp_port = self.get_parameter("tcp_port").get_parameter_value().integer_value
        self.device_name = self.get_parameter("device_name").get_parameter_value().string_value
        self.retry_interval = self.get_parameter("retry_interval").get_parameter_value().double_value

        self._shutdown = False
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)

        self.run_socat_with_retry()

    def _signal_handler(self, sig, frame):
        self._shutdown = True

    def run_socat_with_retry(self):
        cfg_params = ["pty"]
        cfg_params.append("link=" + self.device_name)
        cfg_params.append("raw")
        cfg_params.append("ignoreeof")
        cfg_params.append("waitslave")

        cmd = ["socat"]
        cmd.append(",".join(cfg_params))
        cmd.append(":".join(["tcp", self.robot_ip, str(self.tcp_port)]))

        self.get_logger().info(f"Will connect socat to {self.robot_ip}:{self.tcp_port}")
        self.get_logger().info(f"Command: {' '.join(cmd)}")

        attempt = 0
        while not self._shutdown:
            attempt += 1
            self.get_logger().info(
                f"Attempt {attempt}: Connecting to {self.robot_ip}:{self.tcp_port}..."
            )
            ret = subprocess.call(cmd)
            if self._shutdown:
                break
            if ret == 0:
                self.get_logger().info("socat exited cleanly, restarting...")
            else:
                self.get_logger().warn(
                    f"socat exited with code {ret}. "
                    f"Retrying in {self.retry_interval}s... "
                    f"(Is External Control running on the pendant?)"
                )
            time.sleep(self.retry_interval)

        self.get_logger().info("Shutting down tool communication wrapper.")


def main():
    rclpy.init()
    node = ToolCommunicationWrapper()
    rclpy.shutdown()


if __name__ == "__main__":
    main()
