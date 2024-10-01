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

  // Ensure message contains data for a specific channel
  if (message.data) {
    for (const channel in message.data) {
      const channelData = message.data[channel];

      // Retrieve the corresponding track info div for this channel
      const trackInfoDiv = document.getElementById(
        `track-info-${channel}`
      );
      const trackTitle = document.getElementById(
        `track-title-${channel}`
      );
      const trackArtist = document.getElementById(
        `track-artist-${channel}`
      );
      const trackDuration = document.getElementById(
        `track-duration-${channel}`
      );
      const trackSpeed = document.getElementById(
        `track-speed-${channel}`
      );
      const trackPosition = document.getElementById(
        `track-position-${channel}`
      );
      const trackVolume = document.getElementById(
        `track-volume-${channel}`
      );

      // Update the track title and artist
      if (channelData.data) {
        const data = channelData.data;

        trackTitle.textContent = data.title
          ? `Title: ${data.title}`
          : '';
        trackArtist.textContent = data.artist
          ? `Artist: ${data.artist}`
          : '';

        // Update duration, speed, position, and volume
        trackDuration.textContent = `Duration: ${
          data.duration ? data.duration.toFixed(2) : ''
        }`;
        trackSpeed.textContent = `Speed: ${
          data.speed ? data.speed.toFixed(2) : ''
        }`;
        trackPosition.textContent = `Position: ${
          data.position ? data.position.toFixed(2) : ''
        }`;
        trackVolume.textContent = `Volume: ${
          data.volume ? data.volume.toFixed(2) : ''
        }`;

        // Show track info if the channel is playing
        trackInfoDiv.style.display = "block";
      } else {
        // Handle case where data is null for this channel
        trackTitle.textContent = '';
        trackArtist.textContent = '';
        trackDuration.textContent = 'Duration: ';
        trackSpeed.textContent = 'Speed: ';
        trackPosition.textContent = 'Position: ';
        trackVolume.textContent = 'Volume: ';
        // trackInfoDiv.style.display = 'none'; // Hide if no data
      }
    }
  }
}

document.addEventListener('DOMContentLoaded', () => {
  // Initialize all lock buttons and inputs for both channels
  for (let channel = 1; channel <= 2; channel++) {
    const lockButtons = document.querySelectorAll(
      `.lock-btn-${channel}`
    );
    lockButtons.forEach((button) => {
      button.textContent = '🔓'; // Set initial unlocked state
      button.dataset.locked = 'false';
      button.addEventListener('click', toggleLock);
      button.addEventListener('touchend', (event) => {
        event.preventDefault();
        toggleLock.call(button);
      });
    });

    // Enable all input fields related to this channel
    const inputs = document.querySelectorAll(`.input-${channel}`);
    inputs.forEach((input) => {
      input.disabled = false;
      input.style.opacity = '1';
    });
  }
});

// Object to hold lock states for each effect
const effectLocks = {
  'fade-in-duration-1': true,
  'fade-out-duration-1': true,
  'speed-1': true,
  'fade-in-duration-2': true,
  'fade-out-duration-2': true,
  'speed-2': true,
};

// Toggle lock function
function toggleLock() {
  const channel = this.classList.contains('lock-btn-1') ? '1' : '2';
  console.log('Toggling lock for channel', channel);
  const inputs = this.parentElement.querySelectorAll(
    `.input-${channel}`
  );
  console.log('Inputs:', inputs);
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

function setEffects(channel) {
  const fadeInInput = document.getElementById(
    `fade-in-duration-${channel}`
  );
  const fadeInApplyAfterInput = document.getElementById(
    `fade-in-apply-after-${channel}`
  );
  const fadeOutInput = document.getElementById(
    `fade-out-duration-${channel}`
  );
  const fadeOutApplyAfterInput = document.getElementById(
    `fade-out-apply-after-${channel}`
  );
  const speedInput = document.getElementById(`speed-${channel}`);
  const speedDurationInput = document.getElementById(
    `speed-duration-${channel}`
  );
  const speedApplyAfterInput = document.getElementById(
    `speed-apply-after-${channel}`
  );

  const effectsData = {
    event: 'effects',
    channel: channel,
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

  document
    .querySelectorAll(`#effects-container-${channel} input`)
    .forEach((input) => {
      input.disabled = true;
    });

  document.getElementById(
    `effects-container-${channel}`
  ).style.display = 'none';
}

// function sendMessage(message) {
//   console.log('Sending message:', message);
//   socket.send(JSON.stringify(message));
// }

document
  .getElementById('set-effects-btn-1')
  .addEventListener('click', () => setEffects(1));
document
  .getElementById('set-effects-btn-1')
  .addEventListener('touchend', (event) => {
    event.preventDefault();
    setEffects(1);
  });

document
  .getElementById('set-effects-btn-2')
  .addEventListener('click', () => setEffects(2));
document
  .getElementById('set-effects-btn-2')
  .addEventListener('touchend', (event) => {
    event.preventDefault();
    setEffects(2);
  });

// Function to send audio control commands for a specific channel
function sendAudioControl(channel, action) {
  const controlData = {
    event: 'audio_control',
    channel: channel,
    data: action,
  };
  socket.send(JSON.stringify(controlData));
}

// Play button event listeners for each channel
for (let channel = 1; channel <= 2; channel++) {
  document
    .getElementById(`play-btn-${channel}`)
    .addEventListener('click', () => {
      sendAudioControl(channel, 'play');
    });

  document
    .getElementById(`play-btn-${channel}`)
    .addEventListener('touchstart', (event) => {
      event.preventDefault();
      sendAudioControl(channel, 'play');
    });
}

// Pause button event listeners for each channel
for (let channel = 1; channel <= 2; channel++) {
  document
    .getElementById(`pause-btn-${channel}`)
    .addEventListener('click', () => {
      sendAudioControl(channel, 'pause');
    });

  document
    .getElementById(`pause-btn-${channel}`)
    .addEventListener('touchstart', (event) => {
      event.preventDefault();
      sendAudioControl(channel, 'pause');
    });
}

// Stop button event listeners for each channel
for (let channel = 1; channel <= 2; channel++) {
  document
    .getElementById(`stop-btn-${channel}`)
    .addEventListener('click', () => {
      sendAudioControl(channel, 'stop');
    });

  document
    .getElementById(`stop-btn-${channel}`)
    .addEventListener('touchstart', (event) => {
      event.preventDefault();
      sendAudioControl(channel, 'stop');
    });
}
function toggleAutoplay(channel) {
  const autoplayBtn = document.getElementById(
    `autoplay-btn-${channel}`
  );
  const isAutoplay = autoplayBtn.dataset.autoplay === 'true';

  autoplayBtn.dataset.autoplay = !isAutoplay;
  const newAutoplayState = !isAutoplay;

  autoplayBtn.textContent = newAutoplayState
    ? 'Autoplay: On'
    : 'Autoplay: Off';

  const autoplayData = {
    event: 'audio_control',
    channel: channel,
    data: newAutoplayState ? 'autoplay_on' : 'autoplay_off',
  };

  socket.send(JSON.stringify(autoplayData));
}

for (let channel = 1; channel <= 2; channel++) {
  document
    .getElementById(`autoplay-btn-${channel}`)
    .addEventListener('click', () => {
      toggleAutoplay(channel);
    });
}

// Volume slider event listeners for each channel
for (let channel = 1; channel <= 2; channel++) {
  const volumeSlider = document.getElementById(
    `volume-slider-${channel}`
  );
  volumeSlider.addEventListener('mouseup', () => {
    const volume = volumeSlider.value; // Get the current volume value
    sendVolumeControl(channel, volume); // Send volume control data
    document.getElementById(
      `track-volume-${channel}`
    ).textContent = `Volume: ${volume}`;
  });
}

// Function to send volume control commands for a specific channel
function sendVolumeControl(channel, volume) {
  const volumeData = {
    event: 'audio_control',
    channel: channel,
    data: {
      type: 'volume',
      value: volume,
    },
  };
  socket.send(JSON.stringify(volumeData));
}
