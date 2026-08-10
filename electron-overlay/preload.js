const { ipcRenderer } = require('electron');

window.addEventListener('DOMContentLoaded', () => {
  // Expose panic toggle to renderer
  ipcRenderer.on('panic-toggle', () => {
    window.postMessage({ type: 'panic-toggle' }, '*');
  });
});

