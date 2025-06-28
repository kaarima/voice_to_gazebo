const socket = io();

// Elements
const statusEl = document.getElementById('status');
const lastCommandEl = document.getElementById('last-command');
const batteryEl = document.getElementById('battery');
const positionEl = document.getElementById('position');
const voiceBtn = document.getElementById('voice-btn');
const voiceBtnLabel = document.getElementById('voice-btn-label');
const voiceStatus = document.getElementById('voice-status');

// Update robot state UI
socket.on('robot_state', (state) => {
  statusEl.textContent = state.status.charAt(0).toUpperCase() + state.status.slice(1);
  lastCommandEl.textContent = state.lastCommand || 'None';
  batteryEl.textContent = state.battery + '%';
  positionEl.textContent = `(${state.position.x}, ${state.position.y}, ${state.position.theta}°)`;
});

// Voice recognition
let recognizing = false;
let recognition;
if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
  const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
  recognition = new SpeechRecognition();
  recognition.lang = 'en-US';
  recognition.interimResults = false;
  recognition.maxAlternatives = 1;

  recognition.onstart = () => {
    recognizing = true;
    voiceBtnLabel.textContent = 'Listening...';
    voiceStatus.textContent = 'Speak your command.';
  };
  recognition.onend = () => {
    recognizing = false;
    voiceBtnLabel.textContent = 'Send Voice Command';
    voiceStatus.textContent = '';
  };
  recognition.onerror = (e) => {
    recognizing = false;
    voiceBtnLabel.textContent = 'Send Voice Command';
    voiceStatus.textContent = 'Error: ' + e.error;
  };
  recognition.onresult = (event) => {
    const command = event.results[0][0].transcript;
    voiceStatus.textContent = `Heard: "${command}"`;
    socket.emit('voice_command', command);
  };

  voiceBtn.onclick = () => {
    if (!recognizing) {
      recognition.start();
    } else {
      recognition.stop();
    }
  };
} else {
  voiceBtn.disabled = true;
  voiceBtnLabel.textContent = 'Voice not supported';
  voiceStatus.textContent = 'Your browser does not support speech recognition.';
} 