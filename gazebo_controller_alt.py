#!/usr/bin/env python3

import socket
import threading
import time
import re

# Try different import patterns for Gazebo Harmonic
try:
    from gz.msgs10.twist_pb2 import Twist  # type: ignore
    from gz.transport13 import Node
    print("Using gz imports")
except ImportError:
    try:
        from ignition.msgs import Twist  # type: ignore
        from ignition.transport import Node  # type: ignore
        print("Using ignition imports")
    except ImportError:
        print("Warning: Could not import Gazebo bindings. Using mock classes for testing")
        # Fallback mock classes for testing
        class MockVector3:
            def __init__(self):
                self.x = 0.0
                self.y = 0.0
                self.z = 0.0
        
        class Twist:
            def __init__(self):
                self.linear = MockVector3()
                self.angular = MockVector3()
        
        class Node:
            def __init__(self):
                pass
            def advertise(self, topic, msg_type):
                return MockPublisher()
        
        class MockPublisher:
            def publish(self, msg):
                print(f"Mock publish to /cmd_vel: linear.x={msg.linear.x}, angular.z={msg.angular.z}")

class GazeboController:
    def __init__(self, host='127.0.0.1', port=65432):
        self.host = host
        self.port = port
        self.running = False
        
        # Gazebo transport node
        self.node = Node()
        
        # Robot parameters
        self.linear_speed = 1.0  # m/s
        self.angular_speed = 1.0  # rad/s
        self.wheel_separation = 1.2  # m (from SDF)
        self.wheel_radius = 0.4  # m (from SDF)
        
        # Command patterns
        self.command_patterns = {
            r'forward\s+(\d+(?:\.\d+)?)\s*(?:cm|centimeters?)': self.move_forward,
            r'backward\s+(\d+(?:\.\d+)?)\s*(?:cm|centimeters?)': self.move_backward,
            r'left\s+(\d+(?:\.\d+)?)\s*(?:degrees?|deg)': self.turn_left,
            r'right\s+(\d+(?:\.\d+)?)\s*(?:degrees?|deg)': self.turn_right,
            r'stop': self.stop_robot,
            r'halt': self.stop_robot,
            r'wait': self.stop_robot
        }
        
        # Publisher for velocity commands
        self.cmd_vel_pub = self.node.advertise('cmd_vel', Twist)
        
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
                    if len(match.groups()) > 0:
                        value = float(match.group(1))
                        handler(value)
                    else:
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
            twist_msg = Twist()
            twist_msg.linear.x = linear_x
            twist_msg.angular.z = angular_z
            
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
            
    def move_forward(self, distance_cm):
        """Move robot forward by specified distance in cm"""
        distance_m = distance_cm / 100.0
        duration = distance_m / self.linear_speed
        print(f"Moving forward {distance_cm}cm ({distance_m}m) for {duration:.2f}s")
        self.send_velocity(linear_x=self.linear_speed, duration=duration)
        
    def move_backward(self, distance_cm):
        """Move robot backward by specified distance in cm"""
        distance_m = distance_cm / 100.0
        duration = distance_m / self.linear_speed
        print(f"Moving backward {distance_cm}cm ({distance_m}m) for {duration:.2f}s")
        self.send_velocity(linear_x=-self.linear_speed, duration=duration)
        
    def turn_left(self, degrees):
        """Turn robot left by specified degrees"""
        radians = degrees * 3.14159 / 180.0
        duration = radians / self.angular_speed
        print(f"Turning left {degrees}° ({radians:.2f}rad) for {duration:.2f}s")
        self.send_velocity(angular_z=self.angular_speed, duration=duration)
        
    def turn_right(self, degrees):
        """Turn robot right by specified degrees"""
        radians = degrees * 3.14159 / 180.0
        duration = radians / self.angular_speed
        print(f"Turning right {degrees}° ({radians:.2f}rad) for {duration:.2f}s")
        self.send_velocity(angular_z=-self.angular_speed, duration=duration)
        
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