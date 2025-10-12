const { desktopCapturer } = require('electron')
const axios = require('axios')

const canvas = document.getElementById('overlayCanvas')
const ctx = canvas.getContext('2d')

async function captureScreen() {
  const sources = await desktopCapturer.getSources({ types: ['screen'] })
  if (!sources || sources.length === 0) return null
  // pick the first screen for prototype
  const source = sources[0]
  try {
    const stream = await navigator.mediaDevices.getUserMedia({
      audio: false,
      video: { mandatory: { chromeMediaSource: 'desktop', chromeMediaSourceId: source.id } }
    })
    const video = document.createElement('video')
    video.srcObject = stream
    await video.play()
    // draw a single frame to canvas
    canvas.width = video.videoWidth
    canvas.height = video.videoHeight
    ctx.drawImage(video, 0, 0)

    // get blob
    const blob = await new Promise(resolve => canvas.toBlob(resolve, 'image/png'))
    stream.getTracks().forEach(t=>t.stop())
    return blob
  } catch (e) {
    console.error('capture failed', e)
    return null
  }
}

async function analyzeAndDraw() {
  const blob = await captureScreen()
  if (!blob) return

  // send to python API (localhost:8000)
  const form = new FormData()
  form.append('screenshot', blob, 'screenshot.png')

  try {
    const res = await axios.post('http://127.0.0.1:8000/analyze', form, { headers: form.getHeaders ? form.getHeaders() : {} })
    const regions = res.data.regions || []
    // clear and draw overlays
    ctx.clearRect(0,0,canvas.width,canvas.height)
    ctx.lineWidth = 4
    regions.forEach(r=>{
      ctx.strokeStyle = r.sensitive ? 'red' : 'lime'
      ctx.strokeRect(r.x, r.y, r.w, r.h)
    })
  } catch (e) {
    console.error('analyze failed', e)
  }
}

// initial run and interval
analyzeAndDraw()
setInterval(analyzeAndDraw, 1500)
