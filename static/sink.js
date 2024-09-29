const protocol = window.location.protocol === 'https:' ? 'wss' : 'ws';
const host = window.location.hostname;
const port = '8000'; // Specify the port you're using for the WebSocket server

const socket = new WebSocket(
  `${protocol}://${host}:${port}/ws/audio`
);

socket.onopen = function () {
  console.log('WebSocket connection established.');
  socket.send(
    JSON.stringify({
      event: 'connect',
      data: window.location.pathname,
    })
  );
};

socket.onmessage = function (event) {
  try {
    const message = JSON.parse(event.data);
    handleMessage(message);
  } catch (error) {
    console.error('Failed to parse JSON:', error);
  }
};

function handleMessage(message) {
  console.log('Processing message:', message);

  if (message.data && message.data.title) {
    document.getElementById(
      'track-title'
    ).textContent = `Title: ${message.data.title}`;
    document.getElementById(
      'track-artist'
    ).textContent = `Artist: ${message.data.artist}`;

    // Helper function to format values
    const formatValue = (value) => {
      const numValue = parseFloat(value); // Convert to number
      return !isNaN(numValue) ? numValue.toFixed(2) : ''; // Limit to 2 decimals or return an empty string
    };

    const duration = formatValue(message.data.duration);
    const speed = formatValue(message.data.speed);
    const position = formatValue(message.data.position);
    const volume = formatValue(message.data.volume);

    document.getElementById(
      'track-duration'
    ).textContent = `Duration: ${duration}`;
    document.getElementById(
      'track-speed'
    ).textContent = `Speed: ${speed}`;
    document.getElementById(
      'track-position'
    ).textContent = `Position: ${position}`;
    document.getElementById(
      'track-volume'
    ).textContent = `Volume: ${volume}`;

    document.getElementById('track-info').style.display = 'block';
  }
}

document
  .getElementById('volume-slider')
  .addEventListener('input', function () {
    const volumeValue = parseFloat(this.value).toFixed(2);
    document.getElementById('volume-value').textContent = volumeValue;

    const volumeChangeEvent = {
      event: 'audio_control',
      data: {
        type: 'volume',
        value: volumeValue,
      },
    };

    sendMessage(volumeChangeEvent);
  });

document
  .getElementById('speed-slider')
  .addEventListener('mouseup', function () {
    const speedValue = parseFloat(this.value).toFixed(2);
    document.getElementById('speed-value').textContent = speedValue;

    const speedChangeEvent = {
      event: 'audio_control',
      data: {
        type: 'speed',
        value: speedValue,
      },
    };

    sendMessage(speedChangeEvent);
  });

function sendMessage(message) {
  console.log('Sending message:', message);
  socket.send(JSON.stringify(message));
}

// Control buttons
document.getElementById('play-btn').addEventListener('click', () => {
  const playData = { event: 'audio_control', data: 'play' };
  socket.send(JSON.stringify(playData));
});

document.getElementById('pause-btn').addEventListener('click', () => {
  const pauseData = { event: 'audio_control', data: 'pause' };
  socket.send(JSON.stringify(pauseData));
});

document.getElementById('stop-btn').addEventListener('click', () => {
  const stopData = { event: 'audio_control', data: 'stop' };
  socket.send(JSON.stringify(stopData));
});
