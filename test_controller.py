#!/usr/bin/env python3

import socket
import threading
import time
import re

class MockGazeboController:
    """Mock controller for testing without Gazebo"""
    
    def __init__(self, host='127.0.0.1', port=65432):
        self.host = host
        self.port = port
        self.running = False
        
        # Robot parameters
        self.linear_speed = 1.0  # m/s
        self.angular_speed = 1.0  # rad/s
        
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
        
    def start_server(self):
        """Start TCP server to listen for commands from Node.js"""
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(1)
        
        print(f"Mock Gazebo controller listening on {self.host}:{self.port}")
        print("This is a test version - no actual Gazebo commands will be sent")
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
        
    def move_forward(self, distance_cm):
        """Move robot forward by specified distance in cm"""
        distance_m = distance_cm / 100.0
        duration = distance_m / self.linear_speed
        print(f"[MOCK] Moving forward {distance_cm}cm ({distance_m}m) for {duration:.2f}s")
        print(f"[MOCK] Would send: linear.x={self.linear_speed}, angular.z=0.0")
        time.sleep(0.5)  # Simulate movement time
        print(f"[MOCK] Would send: linear.x=0.0, angular.z=0.0 (stop)")
        
    def move_backward(self, distance_cm):
        """Move robot backward by specified distance in cm"""
        distance_m = distance_cm / 100.0
        duration = distance_m / self.linear_speed
        print(f"[MOCK] Moving backward {distance_cm}cm ({distance_m}m) for {duration:.2f}s")
        print(f"[MOCK] Would send: linear.x={-self.linear_speed}, angular.z=0.0")
        time.sleep(0.5)  # Simulate movement time
        print(f"[MOCK] Would send: linear.x=0.0, angular.z=0.0 (stop)")
        
    def turn_left(self, degrees):
        """Turn robot left by specified degrees"""
        radians = degrees * 3.14159 / 180.0
        duration = radians / self.angular_speed
        print(f"[MOCK] Turning left {degrees}° ({radians:.2f}rad) for {duration:.2f}s")
        print(f"[MOCK] Would send: linear.x=0.0, angular.z={self.angular_speed}")
        time.sleep(0.5)  # Simulate movement time
        print(f"[MOCK] Would send: linear.x=0.0, angular.z=0.0 (stop)")
        
    def turn_right(self, degrees):
        """Turn robot right by specified degrees"""
        radians = degrees * 3.14159 / 180.0
        duration = radians / self.angular_speed
        print(f"[MOCK] Turning right {degrees}° ({radians:.2f}rad) for {duration:.2f}s")
        print(f"[MOCK] Would send: linear.x=0.0, angular.z={-self.angular_speed}")
        time.sleep(0.5)  # Simulate movement time
        print(f"[MOCK] Would send: linear.x=0.0, angular.z=0.0 (stop)")
        
    def stop_robot(self):
        """Stop the robot"""
        print("[MOCK] Stopping robot")
        print("[MOCK] Would send: linear.x=0.0, angular.z=0.0")
        
    def shutdown(self):
        """Shutdown the controller"""
        self.running = False
        self.stop_robot()
        if hasattr(self, 'server_socket'):
            self.server_socket.close()

def test_commands():
    """Test command parsing without network"""
    print("Testing command parsing...")
    
    controller = MockGazeboController()
    
    test_commands = [
        "forward 50cm",
        "backward 30cm", 
        "left 90 degrees",
        "right 45 degrees",
        "stop",
        "halt",
        "forward 25.5 centimeters",
        "left 180 deg",
        "unknown command"
    ]
    
    for cmd in test_commands:
        print(f"\n--- Testing: '{cmd}' ---")
        controller.process_command(cmd)

def main():
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "test":
        test_commands()
    else:
        controller = MockGazeboController()
        
        try:
            controller.start_server()
        except KeyboardInterrupt:
            print("\nShutting down...")
        finally:
            controller.shutdown()

if __name__ == "__main__":
    main() 