Electron frontend prototype

Install & run:

1. cd electron-app
2. npm install
3. npm start

This opens a transparent overlay window that captures the primary screen and POSTs a PNG to the Python API at http://127.0.0.1:8000/analyze every 1.5s.

Make sure to start the Python API first (see Backend/text_blocker/README.md)
