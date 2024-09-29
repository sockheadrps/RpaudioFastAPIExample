const protocol = window.location.protocol === 'https:' ? 'wss' : 'ws';
const host = window.location.hostname;
const port = '8000'; // Specify the port you're using for the WebSocket server

const socket = new WebSocket(
  `${protocol}://${host}:${port}/ws/audio`
);

socket.onopen = function () {
  console.log('WebSocket connection established.');
};

socket.onmessage = function (event) {
  console.log('Message from server: ' + event.data);

  // Parse the incoming JSON data
  const message = JSON.parse(event.data);

  // Check if the message contains data with track information
  if (
    message.data &&
    message.data.title &&
    message.data.artist &&
    message.data.duration
  ) {
    // Update the track info display
    document.getElementById(
      'track-title'
    ).textContent = `Title: ${message.data.title}`;
    document.getElementById(
      'track-artist'
    ).textContent = `Artist: ${message.data.artist}`;
    document.getElementById(
      'track-duration'
    ).textContent = `Duration: ${message.data.duration}`;

    // Show the track info section
    document.getElementById('track-info').style.display = 'block';

    // Hide the effects container if it's visible
    document.getElementById('effects-container').style.display =
      'none';
  }
};

document.addEventListener('DOMContentLoaded', () => {
  document.querySelectorAll('.lock-btn').forEach((button) => {
    button.textContent = '🔓';
    button.dataset.locked = 'false';
  });

  const inputs = document.querySelectorAll('input');
  inputs.forEach((input) => {
    input.disabled = false;
    input.style.opacity = '1';
  });
});

const effectLocks = {
  fadeIn: true,
  fadeOut: true,
  speed: true,
};

document.querySelectorAll('.lock-btn').forEach((button) => {
  button.addEventListener('click', toggleLock);
  button.addEventListener('touchend', (event) => {
    event.preventDefault();
    toggleLock.call(button);
  });
});

function toggleLock() {
  const inputs = this.parentElement.querySelectorAll('input');
  const isLocked = this.dataset.locked === 'true';

  if (isLocked) {
    inputs.forEach((input) => {
      input.disabled = false;
      input.style.opacity = '1';
    });
    this.textContent = '🔓';
    this.dataset.locked = 'false';
    effectLocks[
      this.parentElement.querySelector('label').htmlFor
    ] = false;
  } else {
    inputs.forEach((input) => {
      input.disabled = true;
      input.style.opacity = '0.5';
    });
    this.textContent = '🔒';
    this.dataset.locked = 'true';
    effectLocks[
      this.parentElement.querySelector('label').htmlFor
    ] = true;
  }
}

function setEffects() {
  const fadeInInput = document.getElementById('fade-in-duration');
  const fadeInApplyAfterInput = document.getElementById(
    'fade-in-apply-after'
  );
  const fadeOutInput = document.getElementById('fade-out-duration');
  const fadeOutApplyAfterInput = document.getElementById(
    'fade-out-apply-after'
  );
  const speedInput = document.getElementById('speed');
  const speedDurationInput =
    document.getElementById('speed-duration');
  const speedApplyAfterInput = document.getElementById(
    'speed-apply-after'
  );

  const effectsData = {
    event: 'effects',
    data: {},
  };

  if (!fadeInInput.disabled && fadeInInput.value) {
    const fadeIn = parseFloat(fadeInInput.value);
    const fadeInApplyAfter =
      parseFloat(fadeInApplyAfterInput.value) || 0;
    effectsData.data.fadeInDuration = fadeIn;
    effectsData.data.fadeInApplyAfter = fadeInApplyAfter;
  }

  if (!fadeOutInput.disabled && fadeOutInput.value) {
    const fadeOut = parseFloat(fadeOutInput.value);
    const fadeOutApplyAfter =
      parseFloat(fadeOutApplyAfterInput.value) || 0;
    effectsData.data.fadeOutDuration = fadeOut;
    effectsData.data.fadeOutApplyAfter = fadeOutApplyAfter;
  }

  if (!speedInput.disabled && speedInput.value) {
    const speed = parseFloat(speedInput.value) || 1.0;
    const speedDuration = parseFloat(speedDurationInput.value) || 0;
    const speedApplyAfter =
      parseFloat(speedApplyAfterInput.value) || 0;
    effectsData.data.speed = speed;
    effectsData.data.speedDuration = speedDuration;
    effectsData.data.speedApplyAfter = speedApplyAfter;
  }

  if (Object.keys(effectsData.data).length > 0) {
    socket.send(JSON.stringify(effectsData));
  }

  // Disable the inputs after setting effects
  document
    .querySelectorAll('#effects-container input')
    .forEach((input) => {
      input.disabled = true;
    });

  // Hide the effects container
  document.getElementById('effects-container').style.display = 'none';
}

document
  .getElementById('set-effects-btn')
  .addEventListener('click', setEffects);
document
  .getElementById('set-effects-btn')
  .addEventListener('touchend', (event) => {
    event.preventDefault();
    setEffects();
  });

document.getElementById('pause-btn').addEventListener('click', () => {
  const pauseData = {
    event: 'audio_control',
    data: 'pause',
  };
  socket.send(JSON.stringify(pauseData));
});
document
  .getElementById('pause-btn')
  .addEventListener('touchstart', (event) => {
    event.preventDefault();
    const pauseData = {
      event: 'audio_control',
      data: 'pause',
    };
    socket.send(JSON.stringify(pauseData));
  });

document.getElementById('play-btn').addEventListener('click', () => {
  const playData = {
    event: 'audio_control',
    data: 'play',
  };
  socket.send(JSON.stringify(playData));
});
document
  .getElementById('play-btn')
  .addEventListener('touchstart', (event) => {
    event.preventDefault();
    const playData = {
      event: 'audio_control',
      data: 'play',
    };
    socket.send(JSON.stringify(playData));
  });

document.getElementById('stop-btn').addEventListener('click', () => {
  const stopData = {
    event: 'audio_control',
    data: 'stop',
  };
  socket.send(JSON.stringify(stopData));
});
document
  .getElementById('stop-btn')
  .addEventListener('touchstart', (event) => {
    event.preventDefault();
    const stopData = {
      event: 'audio_control',
      data: 'stop',
    };
    socket.send(JSON.stringify(stopData));
  });

let isAutoplay = false;

document
  .getElementById('autoplay-btn')
  .addEventListener('click', () => {
    isAutoplay = !isAutoplay;

    const autoplayBtn = document.getElementById('autoplay-btn');
    if (isAutoplay) {
      autoplayBtn.textContent = 'Autoplay: On';
      autoplayBtn.dataset.autoplay = 'true';
    } else {
      autoplayBtn.textContent = 'Autoplay: Off';
      autoplayBtn.dataset.autoplay = 'false';
    }

    // Send autoplay state to the server via WebSocket
    const autoplayData = {
      event: 'audio_control',
      data: isAutoplay ? 'autoplay_on' : 'autoplay_off',
    };
    socket.send(JSON.stringify(autoplayData));
  });
