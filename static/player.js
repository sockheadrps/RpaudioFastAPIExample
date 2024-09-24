const socket = new WebSocket('ws://localhost:8000/ws/audio');

socket.onopen = function () {
  console.log('WebSocket connection established.');
};

socket.onmessage = function (event) {
  console.log('Message from server: ' + event.data);
};

// Function to set audio effects and play
function setEffectsAndPlay() {
  const fadeIn =
    parseFloat(document.getElementById('fade-in').value) || 0;
  const fadeOut =
    parseFloat(document.getElementById('fade-out').value) || 0;
  const speed =
    parseFloat(document.getElementById('speed').value) || 1.0;

  // Send the effects settings to the server
  const effectsData = {
    event: 'effects',
    data: {
      fadeIn: fadeIn,
      fadeOut: fadeOut,
      speed: speed,
    },
  };

  socket.send(JSON.stringify(effectsData));

  // Disable the effects input fields
  document
    .getElementById('effects-form')
    .querySelectorAll('input')
    .forEach((input) => {
      input.disabled = true;
    });
}

// Event listeners for buttons
document.getElementById('play-btn').addEventListener('click', () => {
  const playData = {
    event: 'audio_control',
    data: 'play',
  };
  socket.send(JSON.stringify(playData));
});

document.getElementById('pause-btn').addEventListener('click', () => {
  const pauseData = {
    event: 'audio_control',
    data: 'pause',
  };
  socket.send(JSON.stringify(pauseData));
});

document.getElementById('stop-btn').addEventListener('click', () => {
  const stopData = {
    event: 'audio_control',
    data: 'stop',
  };
  socket.send(JSON.stringify(stopData));
});

// Event listener for the set effects button
document
  .getElementById('set-effects-btn')
  .addEventListener('click', function () {
    const fadeInDuration = document.getElementById(
      'fade-in-duration'
    ).value;
    const fadeInApplyAfter = document.getElementById(
      'fade-in-apply-after'
    ).value;
    const fadeOutDuration = document.getElementById(
      'fade-out-duration'
    ).value;
    const fadeOutApplyAfter = document.getElementById(
      'fade-out-apply-after'
    ).value;
    const speed = document.getElementById('speed').value;
    const speedDuration = document.getElementById('speed-duration').value; // New line for speed duration
    const speedApplyAfter = document.getElementById(
      'speed-apply-after'
    ).value;

    // Send the effects settings to the server
    const effectsData = {
      event: 'effects',
      data: {
        fadeInDuration: parseFloat(fadeInDuration),
        fadeInApplyAfter: parseFloat(fadeInApplyAfter),
        fadeOutDuration: parseFloat(fadeOutDuration),
        fadeOutApplyAfter: parseFloat(fadeOutApplyAfter),
        speed: parseFloat(speed),
        speedDuration: parseFloat(speedDuration), // Include speed duration in data
        speedApplyAfter: parseFloat(speedApplyAfter),
      },
    };

    socket.send(JSON.stringify(effectsData));

    // Disable the input fields
    document
      .querySelectorAll('#effects-container input')
      .forEach((input) => {
        input.disabled = true;
      });

    // Disable the Set Effects button
    this.disabled = true;
  });
