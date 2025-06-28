# Quick Setup Guide - Voice-Controlled Robot

## 🚀 Get Started in 10 Minutes

This guide will help you set up the voice-controlled robot system quickly.

## 📋 Prerequisites Check

### 1. System Requirements
```bash
# Check Ubuntu version (22.04+ recommended)
lsb_release -a

# Check Python version (3.8+ required)
python3 --version

# Check Node.js version (16+ required)
node --version

# Check if Gazebo is installed
gz --version
```

### 2. Install Missing Dependencies

#### Install Gazebo Harmonic (if not installed)
```bash
# Add Gazebo repository
sudo apt update
sudo apt install software-properties-common
sudo add-apt-repository ppa:gazebo-stable/gazebo-harmonic
sudo apt update

# Install Gazebo Harmonic
sudo apt install gz-harmonic
```

#### Install Python Dependencies
```bash
# Install Gazebo Python bindings
sudo apt install python3-gz-msgs10 python3-gz-transport13

# Install Python packages
pip3 install -r requirements.txt
```

#### Install Node.js Dependencies
```bash
# Install npm packages
npm install
```

## 🎯 Quick Start

### Step 1: Clone and Setup
```bash
# Clone the repository (if not already done)
git clone <your-repo-url>
cd voice_to_gazebo

# Install dependencies
npm install
```

### Step 2: Start the System
```bash
# Make the startup script executable
chmod +x start_system.sh

# Start everything with one command
./start_system.sh
```

**Or start manually in separate terminals:**

**Terminal 1 - Python Controller:**
```bash
python3 gazebo_controller.py
```

**Terminal 2 - Web Server:**
```bash
npm start
```

**Terminal 3 - Gazebo Simulation:**
```bash
gz sim fixed_robot_world.sdf
```

### Step 3: Test the System
1. **Open your browser** and go to `http://localhost:3000`
2. **Allow microphone access** when prompted
3. **Click the microphone button**
4. **Try these commands:**
   - Say **"forward"** - Robot moves forward 4.5 meters
   - Say **"left"** - Robot turns left
   - Say **"right"** - Robot turns right
   - Say **"backwards"** - Robot moves backward
   - Say **"stop"** - Robot stops

## 🔧 Troubleshooting Common Issues

### Issue 1: "Address already in use"
```bash
# Kill existing processes
pkill -f "python3 gazebo_controller"
pkill -f "node server.js"
pkill -f "gz sim"

# Wait a moment, then restart
sleep 3
./start_system.sh
```

### Issue 2: "Import error" for Gazebo
```bash
# Install Gazebo Python bindings
sudo apt install python3-gz-msgs10 python3-gz-transport13

# Or try the alternative controller
python3 gazebo_controller_alt.py
```

### Issue 3: Voice not recognized
- **Use Chrome browser** (best speech recognition support)
- **Check microphone permissions** in browser settings
- **Speak clearly** and use exact commands: "forward", "left", "right", "backwards"
- **Try different microphone** if available

### Issue 4: Robot not moving
```bash
# Check if Gazebo is running
ps aux | grep "gz sim"

# Check if topics exist
gz topic -l | grep cmd_vel

# Test manual command
gz topic -t /cmd_vel -m gz.msgs.Twist -p 'linear: {x: 1.0}'
```

### Issue 5: Web interface not loading
```bash
# Check if Node.js server is running
ps aux | grep "node server.js"

# Check port 3000
netstat -tlnp | grep 3000

# Restart server
npm start
```

## 📊 System Status Check

### Verify All Components Are Running
```bash
# Check all processes
ps aux | grep -E "(python3 gazebo_controller|node server.js|gz sim)" | grep -v grep

# Expected output should show:
# - python3 gazebo_controller.py
# - node server.js  
# - gz sim server
# - gz sim gui
```

### Test Communication
```bash
# Test web server
curl -s http://localhost:3000 | head -5

# Test Python controller
echo "forward" | nc localhost 65432

# Monitor Gazebo topics
gz topic -e -t /cmd_vel &
```

## 🎮 Voice Commands Reference

| Command | Action | Duration | Distance |
|---------|--------|----------|----------|
| `"forward"` | Move forward | 3.0s | 4.5 meters |
| `"backwards"` | Move backward | 3.0s | 4.5 meters |
| `"left"` | Turn left | 1.5s | ~69° |
| `"right"` | Turn right | 1.5s | ~69° |
| `"stop"` | Stop immediately | - | - |

## 🔍 Debug Mode

### Enable Verbose Logging
```bash
# Run with debug output
DEBUG=1 python3 gazebo_controller.py
```

### Monitor System Logs
```bash
# Monitor all system activity
tail -f /var/log/syslog | grep -E "(gazebo|python|node)"

# Monitor specific component
tail -f gazebo_controller.log
```

## 📱 Browser Compatibility

| Browser | Speech Recognition | Status |
|---------|-------------------|--------|
| Chrome | ✅ Full support | Recommended |
| Edge | ✅ Full support | Good |
| Firefox | ⚠️ Limited | May work |
| Safari | ❌ No support | Not recommended |

## 🎯 Performance Tips

1. **Use Chrome browser** for best voice recognition
2. **Speak clearly** and use exact command words
3. **Close other applications** to free up system resources
4. **Use wired microphone** for better audio quality
5. **Keep browser tab active** during voice commands

## 🆘 Getting Help

If you're still having issues:

1. **Check the logs** for error messages
2. **Verify all prerequisites** are installed
3. **Try the troubleshooting steps** above
4. **Check the main README.md** for detailed documentation
5. **Review TECHNICAL_DOCS.md** for advanced configuration

## ✅ Success Checklist

- [ ] Gazebo Harmonic installed and working
- [ ] Python controller starts without errors
- [ ] Node.js server runs on port 3000
- [ ] Web interface loads in browser
- [ ] Microphone permissions granted
- [ ] Voice commands are recognized
- [ ] Robot moves in Gazebo simulation
- [ ] All basic commands work (forward, left, right, backwards, stop)

**Congratulations! You now have a working voice-controlled robot! 🎉🤖** 