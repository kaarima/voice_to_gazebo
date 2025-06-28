#!/usr/bin/env python3

import time
from gz.msgs10.twist_pb2 import Twist
from gz.transport13 import Node

def test_publish():
    print("🧪 Testing Gazebo publishing...")
    
    # Create node and publisher
    node = Node()
    pub = node.advertise('/cmd_vel', Twist)
    
    # Wait for connection
    time.sleep(1)
    
    # Test forward command
    print("🔧 Publishing forward command...")
    twist = Twist()
    twist.linear.x = 1.0  # type: ignore
    twist.angular.z = 0.0  # type: ignore
    pub.publish(twist)
    print("✅ Forward command published!")
    
    time.sleep(2)
    
    # Test stop command
    print("🔧 Publishing stop command...")
    twist.linear.x = 0.0  # type: ignore
    twist.angular.z = 0.0  # type: ignore
    pub.publish(twist)
    print("✅ Stop command published!")
    
    print("🎯 Test complete! Check if robot moved in Gazebo.")

if __name__ == "__main__":
    test_publish() 