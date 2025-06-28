#!/usr/bin/env python3

import socket
import threading
import time
import re
from gz.msgs10.twist_pb2 import Twist
from gz.transport13 import Node

class GazeboController:
    def __init__(self, host='127.0.0.1', port=65432):
        self.host = host
        self.port = port
        self.running = False
        
        # Gazebo transport node
        self.node = Node()
        
        # Robot parameters
        self.linear_speed = 1.5  # m/s (increased from 0.5)
        self.angular_speed = 0.8  # rad/s (increased from 0.5)
        self.wheel_separation = 1.2  # m (from SDF)
        self.wheel_radius = 0.4  # m (from SDF)
        
        # Command patterns - simplified for basic movement
        self.command_patterns = {
            r'forward': self.move_forward_simple,
            r'go forward': self.move_forward_simple,
            r'move forward': self.move_forward_simple,
            r'backward': self.move_backward_simple,
            r'go backward': self.move_backward_simple,
            r'move backward': self.move_backward_simple,
            r'back': self.move_backward_simple,
            r'left': self.turn_left_simple,
            r'turn left': self.turn_left_simple,
            r'right': self.turn_right_simple,
            r'turn right': self.turn_right_simple,
            r'stop': self.stop_robot,
            r'halt': self.stop_robot,
            r'wait': self.stop_robot
        }
        
        # Publisher for velocity commands
        self.cmd_vel_pub = self.node.advertise('/cmd_vel', Twist)
        
    def start_server(self):
        """Start TCP server to listen for commands from Node.js"""
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(1)
        
        print(f"Gazebo controller listening on {self.host}:{self.port}")
        self.running = True
        
        while self.running:
            try:
                client_socket, address = self.server_socket.accept()
                print(f"Connected to {address}")
                
                # Handle client in separate thread
                client_thread = threading.Thread(
                    target=self.handle_client, 
                    args=(client_socket,)
                )
                client_thread.daemon = True
                client_thread.start()
                
            except Exception as e:
                if self.running:
                    print(f"Server error: {e}")
                break
                
    def handle_client(self, client_socket):
        """Handle commands from a client"""
        try:
            while self.running:
                data = client_socket.recv(1024)
                if not data:
                    break
                    
                command = data.decode('utf-8').strip()
                print(f"Received command: {command}")
                
                # Process the command
                self.process_command(command)
                
        except Exception as e:
            print(f"Client handling error: {e}")
        finally:
            client_socket.close()
            
    def process_command(self, command):
        """Process voice command and execute corresponding action"""
        command_lower = command.lower()
        
        for pattern, handler in self.command_patterns.items():
            match = re.match(pattern, command_lower)
            if match:
                try:
                    # Simple commands don't need parameters
                    handler()
                    print(f"Executed: {command}")
                    return
                except Exception as e:
                    print(f"Error executing command '{command}': {e}")
                    return
                    
        print(f"Unknown command: {command}")
        
    def send_velocity(self, linear_x=0.0, angular_z=0.0, duration=0.0):
        """Send velocity command to Gazebo"""
        try:
            # Limit maximum duration to prevent going too far
            if duration > 3.0:
                duration = 3.0
                print(f"⚠️  Duration limited to 3.0s for safety")
            
            twist_msg = Twist()
            twist_msg.linear.x = linear_x  # type: ignore
            twist_msg.angular.z = angular_z  # type: ignore
            
            # Debug output - show what we're publishing
            print(f"🔧 PUBLISHING to cmd_vel: linear.x={linear_x}, angular.z={angular_z}")
            
            # Send command
            self.cmd_vel_pub.publish(twist_msg)
            print(f"✅ Command published successfully!")
            
            # If duration specified, wait and then stop
            if duration > 0:
                print(f"⏱️  Waiting {duration:.2f}s before stopping...")
                time.sleep(duration)
                self.stop_robot()
                
        except Exception as e:
            print(f"❌ Error sending velocity command: {e}")
            
    def move_forward_simple(self):
        """Move robot forward for a fixed duration"""
        print(f"Moving forward for 3.0s")
        self.send_velocity(linear_x=self.linear_speed, duration=3.0)
        
    def move_backward_simple(self):
        """Move robot backward for a fixed duration"""
        print(f"Moving backward for 3.0s")
        self.send_velocity(linear_x=-self.linear_speed, duration=3.0)
        
    def turn_left_simple(self):
        """Turn robot left for a fixed duration"""
        print(f"Turning left for 1.5s")
        self.send_velocity(angular_z=self.angular_speed, duration=1.5)
        
    def turn_right_simple(self):
        """Turn robot right for a fixed duration"""
        print(f"Turning right for 1.5s")
        self.send_velocity(angular_z=-self.angular_speed, duration=1.5)
        
    def stop_robot(self):
        """Stop the robot"""
        print("Stopping robot")
        self.send_velocity(linear_x=0.0, angular_z=0.0)
        
    def shutdown(self):
        """Shutdown the controller"""
        self.running = False
        self.stop_robot()
        if hasattr(self, 'server_socket'):
            self.server_socket.close()

def main():
    controller = GazeboController()
    
    try:
        controller.start_server()
    except KeyboardInterrupt:
        print("\nShutting down...")
    finally:
        controller.shutdown()

if __name__ == "__main__":
    main() 