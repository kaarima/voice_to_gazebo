const express = require('express');
const http = require('http');
const { Server } = require('socket.io');
const path = require('path');
const net = require('net');

const app = express();
const server = http.createServer(app);
const io = new Server(server);

// Serve static files
app.use(express.static(path.join(__dirname, 'public')));

// Robot state (example)
let robotState = {
  status: 'idle',
  lastCommand: '',
  battery: 100,
  position: { x: 0, y: 0, theta: 0 }
};

const PYTHON_PORT = 65432;
const PYTHON_HOST = '127.0.0.1';

function sendToPython(command) {
  const client = new net.Socket();
  client.connect(PYTHON_PORT, PYTHON_HOST, function() {
    client.write(command);
    client.end();
  });
  client.on('error', (err) => {
    console.error('Python socket error:', err);
  });
}

io.on('connection', (socket) => {
  // Send current state on connect
  socket.emit('robot_state', robotState);

  // Receive voice command from client
  socket.on('voice_command', (command) => {
    robotState.lastCommand = command;
    robotState.status = 'processing';
    sendToPython(command); // Forward to Python script
    setTimeout(() => {
      robotState.status = 'idle';
      io.emit('robot_state', robotState);
    }, 1000);
    io.emit('robot_state', robotState);
  });
});

const PORT = process.env.PORT || 3000;
server.listen(PORT, () => {
  console.log(`Server running on http://localhost:${PORT}`);
}); 