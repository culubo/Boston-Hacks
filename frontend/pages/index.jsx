import PasswordBlocker from '../src/components/PasswordBlocker'
import Header from '../src/components/Header'
import Footer from '../src/components/Footer'
import PixelText from '../src/components/PixelText'
import { useRef, useState } from 'react'

export default function Home() {
  // position state (px). We'll apply as inline translate for smooth GPU-driven movement.
  const [pos, setPos] = useState({ x: 0, y: 0 })
  const draggingRef = useRef(false)
  const startRef = useRef({ x: 0, y: 0 })

  function onPointerDown(e) {
    // only start drag when primary button or touch
    if (e.button !== undefined && e.button !== 0) return
    // restrict dragging to the top decorative bar area only
    // calculate pointer y relative to the card's top
    const rect = e.currentTarget.getBoundingClientRect()
    const y = e.clientY - rect.top
    // top bar is drawn via ::before with height 30px and a thin top edge 3px
    const topBarHeight = 33
    if (y > topBarHeight) return

    draggingRef.current = true
    // capture pointer so we get events outside the element
    e.currentTarget.setPointerCapture?.(e.pointerId)
    startRef.current = { x: e.clientX - pos.x, y: e.clientY - pos.y }
  }

  function onPointerMove(e) {
    if (!draggingRef.current) return
    const nx = e.clientX - startRef.current.x
    const ny = e.clientY - startRef.current.y
    setPos({ x: nx, y: ny })
  }

  function onPointerUp(e) {
    draggingRef.current = false
    e.currentTarget.releasePointerCapture?.(e.pointerId)
  }

  return (
    <div className="App">
      <Header>
        <div
          className="card card-secret draggable"
          style={{ position: 'relative', transform: `translate(${pos.x}px, ${pos.y}px)` }}
          onPointerDown={onPointerDown}
          onPointerMove={onPointerMove}
          onPointerUp={onPointerUp}
        >
          {/* place the site name inside the top decorative bar */}
          <div className="card-top-text">
            <PixelText text="Boston Hacks" fontSize={16} color="#fff" />
            <button
              type="button"
              className="card-close-btn"
              aria-label="Close"
              onClick={() => console.log('Close clicked')}
            >
              ×
            </button>
          </div>
          {/* beige sub-bar under the blue top bar containing controls */}
          <div className="card-subbar">
            <button
            className="block-screen-btn"
            onClick={async (e) => {
              e.preventDefault();
              try {
                const res = await fetch("http://localhost:5000/block", { method: "POST" });
                const data = await res.json();
                console.log("Backend started:", data);
                alert("Screen blocking started!");
              } catch (err) {
                console.error("Error:", err);
                alert("Failed to start screen blocking.");
              }
            }}
          >
            Block
          </button>

          </div>
          <PasswordBlocker />
        </div>
      </Header>
      <Footer />
    </div>
  )
}
