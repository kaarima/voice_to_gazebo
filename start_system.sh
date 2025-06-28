#!/bin/bash

# Voice to Gazebo Robot Control System Startup Script

echo "🚀 Starting Voice to Gazebo Robot Control System"
echo "================================================"

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to check if a port is in use
port_in_use() {
    netstat -tuln 2>/dev/null | grep -q ":$1 "
}

# Check prerequisites
echo "📋 Checking prerequisites..."

if ! command_exists node; then
    echo "❌ Node.js not found. Please install Node.js 16+"
    exit 1
fi

if ! command_exists python3; then
    echo "❌ Python 3 not found. Please install Python 3.8+"
    exit 1
fi

echo "✅ Prerequisites check passed"

# Check if port 3000 is in use
if port_in_use 3000; then
    echo "⚠️  Port 3000 is already in use. Please stop any existing web server."
    exit 1
fi

# Check if port 65432 is in use
if port_in_use 65432; then
    echo "⚠️  Port 65432 is already in use. Please stop any existing Python controller."
    exit 1
fi

# Install Node.js dependencies if needed
if [ ! -d "node_modules" ]; then
    echo "📦 Installing Node.js dependencies..."
    npm install
fi

# Build CSS if needed
if [ ! -f "public/tailwind.css" ]; then
    echo "🎨 Building CSS..."
    npm run build:css
fi

# Function to cleanup on exit
cleanup() {
    echo ""
    echo "🛑 Shutting down system..."
    if [ ! -z "$NODE_PID" ]; then
        kill $NODE_PID 2>/dev/null
    fi
    if [ ! -z "$PYTHON_PID" ]; then
        kill $PYTHON_PID 2>/dev/null
    fi
    exit 0
}

# Set up signal handlers
trap cleanup SIGINT SIGTERM

echo ""
echo "🎯 Starting components..."

# Start Python controller in background
echo "🐍 Starting Python controller..."
python3 gazebo_controller_alt.py &
PYTHON_PID=$!

# Wait a moment for Python controller to start
sleep 2

# Check if Python controller started successfully
if ! kill -0 $PYTHON_PID 2>/dev/null; then
    echo "❌ Failed to start Python controller"
    echo "💡 Try running: python3 test_controller.py test"
    echo "💡 Or install Gazebo Python bindings: sudo apt install python3-gz-harmonic"
    exit 1
fi

echo "✅ Python controller started (PID: $PYTHON_PID)"

# Start Node.js server in background
echo "🌐 Starting Node.js server..."
npm start &
NODE_PID=$!

# Wait a moment for server to start
sleep 3

# Check if Node.js server started successfully
if ! kill -0 $NODE_PID 2>/dev/null; then
    echo "❌ Failed to start Node.js server"
    kill $PYTHON_PID 2>/dev/null
    exit 1
fi

echo "✅ Node.js server started (PID: $NODE_PID)"

echo ""
echo "🎉 System started successfully!"
echo "================================"
echo "📱 Open your browser and go to: http://localhost:3000"
echo "🎤 Click 'Send Voice Command' and try:"
echo "   • 'forward 50cm'"
echo "   • 'left 90 degrees'"
echo "   • 'stop'"
echo ""
echo "🔧 To stop the system, press Ctrl+C"
echo ""

# Wait for user to stop
wait 