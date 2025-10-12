import React, { useRef, useEffect } from 'react';

export default function PixelText({
  text = 'Boston Hacks',
  width = 250,
  height = 30,
  scale = 2,
  color = '#ffffff',
  bg = 'transparent',
  shadow = { x: 2, y: 0, color: 'rgba(0,0,0,0.6)' } // default right-side hard shadow
}) {
  const canvasRef = useRef(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    // render at a low internal resolution then scale up with CSS
    const ctx = canvas.getContext('2d');
    // internal (low-res) size
    const w = Math.max(32, Math.round(width / scale));
    const h = Math.max(8, Math.round(height / scale));
    canvas.width = w;
    canvas.height = h;
    // clear
    ctx.clearRect(0, 0, w, h);
    // optional background
    if (bg && bg !== 'transparent') {
      ctx.fillStyle = bg;
      ctx.fillRect(0, 0, w, h);
    }
    // draw text scaled to fit the small canvas
    // optionally draw a hard pixel shadow by rendering the text offset first
    if (shadow && (shadow.x || shadow.y)) {
      ctx.fillStyle = shadow.color || 'rgba(0,0,0,0.6)';
      // hard shadow: draw one or two offset copies for a stronger effect
      ctx.fillText(text, x + (shadow.x || 0), y + (shadow.y || 0));
    }
    ctx.fillStyle = color;
    // choose a pixel-friendly font (monospace) and large weight so glyphs are blocky
    const fontSize = Math.floor(h * 0.9);
    ctx.font = `${fontSize}px monospace`;
    ctx.textBaseline = 'middle';
    ctx.textAlign = 'left';
    // measure and scale if necessary
    let metrics = ctx.measureText(text);
    let textW = metrics.width;
    const scaleX = Math.min(1, (w - 2) / textW);
    if (scaleX < 1) {
      // reduce font size to fit
      ctx.font = `${Math.floor(fontSize * scaleX)}px monospace`;
      metrics = ctx.measureText(text);
      textW = metrics.width;
    }
    // center vertically and give a small left padding
    const x = 2;
    const y = h / 2;
    ctx.fillText(text, x, y);

    // force nearest-neighbor scaling when the canvas is scaled up by CSS
    const style = canvas.style;
    style.imageRendering = 'pixelated';
    style.webkitImageRendering = 'pixelated';
    style.msInterpolationMode = 'nearest-neighbor';
  }, [text, width, height, scale, color, bg]);

  // CSS will scale this canvas up by `scale` using transforms or explicit width/height
  return (
    <canvas
      ref={canvasRef}
      className="card-top-pixel"
      width={Math.max(32, Math.round(width / scale))}
      height={Math.max(8, Math.round(height / scale))}
      aria-hidden="true"
    />
  );
}
